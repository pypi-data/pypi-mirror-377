import logging
import unittest

import mock
from mock import call
from mock import patch

from splunk_handler_zuul import SplunkHandler
from pythonjsonlogger import jsonlogger

# These are intentionally different than the kwarg defaults
SPLUNK_HOST = 'splunk-server.example.com'
SPLUNK_PORT = 1234
SPLUNK_TOKEN = '851A5E58-4EF1-7291-F947-F614A76ACB21'
SPLUNK_INDEX = 'test_index'
SPLUNK_HOSTNAME = 'zuul-web-db8db5795-wnk7v'
SPLUNK_SOURCE = 'test_source'
SPLUNK_SOURCETYPE = 'test_sourcetype'
SPLUNK_VERIFY = False
SPLUNK_TIMEOUT = 27
SPLUNK_FLUSH_INTERVAL = .1
SPLUNK_QUEUE_SIZE = 1111
SPLUNK_DEBUG = False
SPLUNK_RETRY_COUNT = 1
SPLUNK_RETRY_BACKOFF = 0.1

RECEIVER_URL = 'https://%s:%s/services/collector' % (SPLUNK_HOST, SPLUNK_PORT)


class TestSplunkHandler(unittest.TestCase):
    def setUp(self):
        self.mock_time = mock.patch('time.time', return_value=10).start()
        self.mock_request = mock.patch('requests.Session.post').start()
        self.splunk = SplunkHandler(
            host=SPLUNK_HOST,
            port=SPLUNK_PORT,
            token=SPLUNK_TOKEN,
            index=SPLUNK_INDEX,
            hostname=SPLUNK_HOSTNAME,
            source=SPLUNK_SOURCE,
            sourcetype=SPLUNK_SOURCETYPE,
            verify=SPLUNK_VERIFY,
            timeout=SPLUNK_TIMEOUT,
            flush_interval=SPLUNK_FLUSH_INTERVAL,
            queue_size=SPLUNK_QUEUE_SIZE,
            debug=SPLUNK_DEBUG,
            retry_count=SPLUNK_RETRY_COUNT,
            record_format=True,
            retry_backoff=SPLUNK_RETRY_BACKOFF,
        )

    def tearDown(self):
        self.splunk = None

    def test_init(self):
        self.assertIsNotNone(self.splunk)
        self.assertIsInstance(self.splunk, SplunkHandler)
        self.assertIsInstance(self.splunk, logging.Handler)
        self.assertEqual(self.splunk.host, SPLUNK_HOST)
        self.assertEqual(self.splunk.port, SPLUNK_PORT)
        self.assertEqual(self.splunk.token, SPLUNK_TOKEN)
        self.assertEqual(self.splunk.index, SPLUNK_INDEX)
        self.assertEqual(self.splunk.hostname, SPLUNK_HOSTNAME)
        self.assertEqual(self.splunk.source, SPLUNK_SOURCE)
        self.assertEqual(self.splunk.sourcetype, SPLUNK_SOURCETYPE)
        self.assertEqual(self.splunk.verify, SPLUNK_VERIFY)
        self.assertEqual(self.splunk.timeout, SPLUNK_TIMEOUT)
        self.assertEqual(self.splunk.flush_interval, SPLUNK_FLUSH_INTERVAL)
        self.assertEqual(self.splunk.max_queue_size, SPLUNK_QUEUE_SIZE)
        self.assertEqual(self.splunk.debug, SPLUNK_DEBUG)
        self.assertEqual(self.splunk.retry_count, SPLUNK_RETRY_COUNT)
        self.assertEqual(self.splunk.retry_backoff, SPLUNK_RETRY_BACKOFF)

        self.assertFalse(logging.getLogger('requests').propagate)
        self.assertFalse(logging.getLogger('splunk_handler_zuul').propagate)

    def test_splunk_worker(self):
        # Silence root logger
        log = logging.getLogger('')
        for h in log.handlers:
            log.removeHandler(h)

        log = logging.getLogger('test')
        for h in log.handlers:
            log.removeHandler(h)

        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(module)s %(message)s')
        self.splunk.setFormatter(formatter)
        log.addHandler(self.splunk)
        log.warning('%s Looking for lost %s', '[e: 8538dc593cf643fea68acb57c6ac12b8]', 'builds')

        self.splunk.timer.join()  # Have to wait for the timer to exec

        expected_output = '{"event": "{\\"asctime\\": \\"1970-01-01 01:00:10,000\\", ' + \
                          '\\"name\\": \\"test\\", \\"levelname\\": \\"WARNING\\", ' + \
                          '\\"module\\": \\"test_splunk_handler\\", ' +\
                          '\\"message\\": ' + \
                          '\\"[e: 8538dc593cf643fea68acb57c6ac12b8] Looking for lost builds\\"}", ' + \
                          '"host": "zuul-web-db8db5795-wnk7v", "index": "test_index", ' \
                          '"source": "%s", "sourcetype": "zuul-web", "time": 10}' % \
                          (SPLUNK_SOURCE)

        self.mock_request.assert_called_once_with(
            RECEIVER_URL,
            verify=SPLUNK_VERIFY,
            data=expected_output,
            timeout=SPLUNK_TIMEOUT,
            headers={'Authorization': "Splunk %s" % SPLUNK_TOKEN},
        )

    def test_splunk_worker_override(self):
        self.splunk.allow_overrides = True

        # Silence root logger
        log = logging.getLogger('')
        for h in log.handlers:
            log.removeHandler(h)

        log = logging.getLogger('test')
        for h in log.handlers:
            log.removeHandler(h)

        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(module)s %(message)s')
        self.splunk.setFormatter(formatter)
        log.addHandler(self.splunk)
        log.warning('hello!', extra={'_time': 5, '_host': 'host', '_index': 'index'})

        self.splunk.timer.join()  # Have to wait for the timer to exec

        expected_output = '{"event": "{\\"asctime\\": \\"1970-01-01 01:00:10,000\\", ' + \
                          '\\"name\\": \\"test\\", \\"levelname\\": \\"WARNING\\", ' + \
                          '\\"module\\": \\"test_splunk_handler\\", ' +\
                          '\\"message\\": \\"hello!\\"}", ' + \
                          '"host": "host", "index": "index", ' \
                          '"source": "%s", "sourcetype": "host", "time": 5}' % \
                          (SPLUNK_SOURCE)

        self.mock_request.assert_called_once_with(
            RECEIVER_URL,
            data=expected_output,
            headers={'Authorization': "Splunk %s" % SPLUNK_TOKEN},
            verify=SPLUNK_VERIFY,
            timeout=SPLUNK_TIMEOUT
        )

    def test_full_queue_error(self):
        self.splunk.allow_overrides = True
        self.splunk.max_queue_size = 10
        mock_write_log = patch.object(self.splunk, 'write_log').start()

        # Silence root logger
        log = logging.getLogger('')
        for h in log.handlers:
            log.removeHandler(h)

        log = logging.getLogger('test')
        for h in log.handlers:
            log.removeHandler(h)

        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(module)s %(message)s')
        self.splunk.setFormatter(formatter)
        log.addHandler(self.splunk)

        for _ in range(20):
            log.warning('hello!', extra={'_time': 5, '_host': 'host', '_index': 'index'})

        self.splunk.timer.join()

        mock_write_log.assert_any_call("Log queue full; log data will be dropped.")

    def test_wait_until_empty_and_keep_ahead(self):
        self.splunk.allow_overrides = True
        self.splunk.force_keep_ahead = True
        self.splunk.max_queue_size = 10
        mock_write_log = patch.object(self.splunk, 'write_log').start()

        # Silence root logger
        log = logging.getLogger('')
        for h in log.handlers:
            log.removeHandler(h)

        log = logging.getLogger('test')
        for h in log.handlers:
            log.removeHandler(h)

        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(module)s %(message)s')
        self.splunk.setFormatter(formatter)
        log.addHandler(self.splunk)

        # without force keep ahead, this would drop logs
        for _ in range(20):
            log.warning('hello!', extra={'_time': 5, '_host': 'host', '_index': 'index'})

        # use wait until empty instead of joining the timer
        # if this doesnt wait correctly, we'd expect to be missing calls to mock_request
        self.splunk.wait_until_empty()

        expected_output = '{"event": "{\\"asctime\\": \\"1970-01-01 01:00:10,000\\", ' + \
                          '\\"name\\": \\"test\\", \\"levelname\\": \\"WARNING\\", ' + \
                          '\\"module\\": \\"test_splunk_handler\\", ' +\
                          '\\"message\\": \\"hello!\\"}", ' + \
                          '"host": "host", "index": "index", ' \
                          '"source": "%s", "sourcetype": "host", "time": 5}' % \
                          (SPLUNK_SOURCE)

        # two batches of 10 messages sent
        self.mock_request.assert_has_calls([call(
            RECEIVER_URL,
            data=expected_output * 10,
            headers={'Authorization': 'Splunk %s' % SPLUNK_TOKEN},
            verify=SPLUNK_VERIFY,
            timeout=SPLUNK_TIMEOUT
        )] * 2, any_order=True)

        # verify no logs dropped
        mock_write_log.assert_not_called()

