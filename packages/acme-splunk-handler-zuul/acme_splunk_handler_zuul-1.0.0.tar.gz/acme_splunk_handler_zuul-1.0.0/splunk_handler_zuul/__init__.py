import atexit
import json
import logging
import socket
import time
import traceback
from threading import Thread

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

instances = []  # For keeping track of running class instances
DEFAULT_QUEUE_SIZE = 5000


# Called when application exit imminent (main thread ended / got kill signal)
@atexit.register
def perform_exit():
    for instance in instances:
        try:
            instance.shutdown()
        except Exception:
            pass


def force_flush():
    for instance in instances:
        try:
            instance.force_flush()
        except Exception:
            pass


def wait_until_empty():
    for instance in instances:
        try:
            instance.wait_until_empty()
        except Exception:
            pass


class SplunkHandler(logging.Handler):
    """
    A logging handler to send events to a Splunk Enterprise instance
    running the Splunk HTTP Event Collector.
    """

    def __init__(self, host, port, token, index,
                 allow_overrides=False, debug=False, flush_interval=15.0,
                 force_keep_ahead=False, hostname=None,
                 protocol='https', proxies=None,
                 queue_size=DEFAULT_QUEUE_SIZE, record_format=False,
                 retry_backoff=2.0, retry_count=5, source=None,
                 sourcetype='text', timeout=60, url=None, verify=True):
        """
        Args:
            host (str): The Splunk host param
            port (int): The port the host is listening on
            token (str): Authentication token
            index (str): Splunk index to write to
            allow_overrides (bool): Whether to look for _<param>
                                    in log data (ex: _index)
            debug (bool): Whether to print debug console messages
            flush_interval (float): How often to push events
                                    to splunk host in seconds
            force_keep_ahead (bool): Sleep instead of dropping
                                     logs when queue fills
            hostname (str): The Splunk Enterprise hostname
            protocol (str): The web protocol to use
            proxies (dict): The proxies to use for the request
            queue_size (int): The max number of logs to queue,
                              set to 0 for no max
            record_format (bool): Whether the log record will be json
            retry_backoff (float): The requests lib backoff factor
            retry_count (int): The number of times to retry a failed request
            source (str): The Splunk source param
            sourcetype (str): The Splunk sourcetype param
            timeout (float): The time to wait for a response from Splunk
            url (str): Override of the url to send the event to
            verify (bool): Whether to perform ssl certificate validation
        """

        global instances
        instances.append(self)
        logging.Handler.__init__(self)

        self.allow_overrides = allow_overrides
        self.host = host
        self.port = port
        self.token = token
        self.index = index
        self.source = source
        self.sourcetype = sourcetype
        self.verify = verify
        self.timeout = timeout
        self.flush_interval = flush_interval
        self.force_keep_ahead = force_keep_ahead
        self.log_payload = ""
        self.SIGTERM = False  # 'True' if application requested exit
        self.timer = None
        # It is possible to get 'behind' and never catch
        # up, so we limit the queue size
        self.queue = list()
        self.max_queue_size = max(queue_size, 0)  # 0 is min queue size
        self.debug = debug
        self.session = requests.Session()
        self.retry_count = retry_count
        self.retry_backoff = retry_backoff
        self.protocol = protocol
        self.proxies = proxies
        self.record_format = record_format
        self.processing_payload = False
        self.running = False
        if not url:
            self.url = '%s://%s:%s/services/collector' % (self.protocol,
                                                          self.host,
                                                          self.port)
        else:
            self.url = url

        # Keep ahead depends on queue size, so cannot be 0
        if self.force_keep_ahead and not self.max_queue_size:
            self.write_log(
                "Cannot keep ahead of unbound queue, using default queue size")
            self.max_queue_size = DEFAULT_QUEUE_SIZE

        self.write_debug_log("Starting debug mode")

        if hostname is None:
            self.hostname = socket.gethostname()
        else:
            self.hostname = hostname

        self.write_debug_log("Preparing to override loggers")

        # prevent infinite recursion by silencing requests and urllib3 loggers
        logging.getLogger('requests').propagate = False
        logging.getLogger('urllib3').propagate = False

        # and do the same for ourselves
        logging.getLogger(__name__).propagate = False

        # disable all warnings from urllib3 package
        if not self.verify:
            requests.packages.urllib3.disable_warnings()

        if self.verify and self.protocol == 'http':
            print("[SplunkHandler DEBUG] "
                  + 'cannot use SSL Verify and unsecure connection')

        if self.proxies is not None:
            self.session.proxies = self.proxies

        # Set up automatic retry with back-off
        self.write_debug_log("Preparing to create a Requests session")
        retry = Retry(total=self.retry_count,
                      backoff_factor=self.retry_backoff,
                      allowed_methods=None,  # Retry for any HTTP verb
                      status_forcelist=[500, 502, 503, 504])
        self.session.mount(self.protocol
                           + '://', HTTPAdapter(max_retries=retry))

        self.worker_thread = None
        self.start_worker_thread()

        self.write_debug_log("Class initialize complete")

    def emit(self, record):
        self.write_debug_log("emit() called")

        try:
            record = self.format_record(record)
        except Exception as e:
            self.write_log("Exception in Splunk logging handler: %s" % str(e))
            self.write_log(traceback.format_exc())
            return

        if self.flush_interval <= 0:
            # Flush log immediately; is blocking call
            self._send_payload(payload=record)
            return

        self.write_debug_log("Writing record to log queue")

        # If force keep ahead, sleep until space
        # in queue to prevent falling behind
        while self.force_keep_ahead and len(self.queue) >= self.max_queue_size:
            time.sleep(self.alt_flush_interval)

        # Put log message into queue; worker thread will pick up
        if not self.max_queue_size or len(self.queue) < self.max_queue_size:
            self.queue.append(record)
        else:
            self.write_log("Log queue full; log data will be dropped.")

    def close(self):
        self.shutdown()
        logging.Handler.close(self)

    #
    # helper methods
    #

    def start_worker_thread(self):
        # Start a worker thread responsible for sending logs

        self.write_debug_log("Starting worker thread.")
        self.worker_thread = Thread(target=self._splunk_worker)
        # Auto-kill thread if main process exits
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def write_log(self, log_message):
        print("[SplunkHandler] " + log_message)

    def write_debug_log(self, log_message):
        if self.debug:
            print("[SplunkHandler DEBUG] " + log_message)

    def format_record(self, record):
        self.write_debug_log("format_record() called")
        params = {
            'time': self.getsplunkattr(record, '_time', time.time()),
            'host': self.getsplunkattr(record, '_host', self.hostname),
            'index': self.getsplunkattr(record, '_index', self.index),
            'source': record.pathname if self.source is None else self.source
            }

        params['sourcetype'] = self.getServiceName(params.get('host'))
        params['event'] = self.format(record)

        self.write_debug_log("Record dictionary created")

        formatted_record = json.dumps(params, sort_keys=True)
        self.write_debug_log("Record formatting complete")

        return formatted_record

    def getServiceName(self, hostname):
        service_group = hostname.split('-')
        if len(service_group) > 2:
            return service_group[0] + '-' + service_group[1]
        else:
            return hostname

    def getsplunkattr(self, obj, attr, default=None):
        val = default
        if self.allow_overrides:
            val = getattr(obj, attr, default)
            try:
                delattr(obj, attr)
            except Exception:
                pass
        return val

    def _send_payload(self, payload):
        r = self.session.post(
            self.url,
            data=payload,
            headers={'Authorization': "Splunk %s" % self.token},
            verify=self.verify,
            timeout=self.timeout
        )
        r.raise_for_status()  # Throws exception for 4xx/5xx status

    def _flush_logs(self):
        self.processing_payload = True
        payload = self.empty_queue()

        if payload:
            self.write_debug_log("Payload available for sending")
            self.write_debug_log("Destination URL is " + self.url)

            try:
                self.write_debug_log("Sending payload: " + payload)
                self._send_payload(payload)
                self.write_debug_log("Payload sent successfully")
            except Exception as e:
                try:
                    self.write_log(
                        "Exception in Splunk logging handler: %s" % str(e))
                    self.write_log(traceback.format_exc())
                except Exception:
                    self.write_debug_log(
                        "Exception encountered," +
                        "but traceback could not be formatted"
                    )
        else:
            self.write_debug_log("No payload was available to send")
        self.processing_payload = False

    def _splunk_worker(self):
        time_end = 0
        time_start = 0
        self.running = True
        while self.running:
            sleep_amount = self.flush_interval - (time_end - time_start)
            time.sleep(max(sleep_amount, 0))
            time_start = time.time()
            self._flush_logs()

            if self.SIGTERM:
                self.write_debug_log(
                    "Timer reset aborted due to SIGTERM received")
                self.running = False

            time_end = time.time()

    def empty_queue(self):
        if len(self.queue) == 0:
            self.write_debug_log("Queue was empty")
            return ""

        self.write_debug_log("Creating payload")
        log_payload = ""
        if self.SIGTERM:
            log_payload += ''.join(self.queue)
            self.queue.clear()
        else:
            # without looking at each item,
            # estimate how many can fit in 50 MB
            apprx_size_base = len(self.queue[0])
            # dont eval max/event size ration as less than 1
            # dont count more than what is in queue
            # to ensure the same number as pulled are deleted
            # Note (avass): 524288 is 50MB/100
            count = min(max(int(524288 / apprx_size_base), 1), len(self.queue))
            log_payload += ''.join(self.queue[:count])
            del self.queue[:count]
        self.write_debug_log("Queue task completed")

        return log_payload

    def force_flush(self):
        self.write_debug_log("Force flush requested")
        self._flush_logs()
        self.wait_until_empty()  # guarantees queue is emptied

    def shutdown(self):
        self.write_debug_log("Immediate shutdown requested")

        # Only initiate shutdown once
        if self.SIGTERM:
            return

        self.write_debug_log("Setting instance SIGTERM=True")
        self.running = False
        self.SIGTERM = True

        self.write_debug_log(
            "Starting up the final run of the worker thread before shutdown")
        # Send the remaining items that might be sitting in queue.
        self._flush_logs()
        self.wait_until_empty()  # guarantees queue is emptied before exit

    def wait_until_empty(self):
        self.write_debug_log("Waiting until queue empty")
        while len(self.queue) > 0 or self.processing_payload:
            self.write_debug_log("Current queue size: " + str(len(self.queue)))
            time.sleep(self.alt_flush_interval)

    @property
    def alt_flush_interval(self):
        return min(1.0, self.flush_interval / 2)
