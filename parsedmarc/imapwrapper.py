import errno
import imaplib
import logging
import socket

from mailsuite.imap import IMAPClient

logging.basicConfig(
    format='%(levelname)8s:%(filename)s:%(lineno)d:'
           '%(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S')

logger = logging.getLogger("parsedmarc")

class ImapWrapper:
    client = None

    def __init__(self, host, username, password, port=None, ssl=True,
                 verify=True, timeout=30, max_retries=4,
                 initial_folder="INBOX", idle_callback=None, idle_timeout=30):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssl = ssl
        self.verify = verify
        self.timeout = timeout
        self.max_retries = max_retries
        self.initial_folder = initial_folder
        self.idle_callback = idle_callback
        self.idle_timeout = idle_timeout
        self._connect()

    def _connect(self):
        logger.debug('_connect')
        if self.client:
            try:
                self._test_connection()
            except (BrokenPipeError, imaplib.IMAP4.abort) as e:
                logger.debug('Exception caught (%s) %s', type(e), str(e))
                logger.debug('Starting reset_connection()')
                self.client.reset_connection()
                logger.debug('Finished reset_connection()')
        else:
            logger.debug('Connecting...')
            self.client = IMAPClient(self.host, self.username, self.password,
                                     port=self.port,
                                     ssl=self.ssl,
                                     verify=self.verify,
                                     timeout=self.timeout,
                                     max_retries=self.max_retries,
                                     initial_folder=self.initial_folder)
    def _test_connection(self):
        logger.debug('_test_connection')
        self.client.noop()

    def move_messages(self, msg_uids, folder_path, _attempt=1):
        logger.debug('move_messages')
        self._connect()
        try:
            logger.debug('Starting move_messages()')
            self.client.move_messages(msg_uids, folder_path, _attempt)
            logger.debug('Finished move_messages()')
        except Exception as e:
            logger.debug('Exception caught when moving message: %s' % str(e))
            raise e

    def create_folder(self, folder_path, _attempt=1):
        logger.debug('create_folder')
        self._connect()
        return self.client.create_folder(folder_path, _attempt)

    def search(self, criteria="ALL", charset=None):
        logger.debug('search')
        self._connect()
        return self.client.search(criteria, charset)

    def fetch_message(self, msg_uid, parse=False, _attempt=1):
        logger.debug('fetch_message')
        self._connect()
        return self.client.fetch_message(msg_uid, parse, _attempt)

    def delete_messages(self, messages, silent=False):
        logger.debug('delete_messages')
        self._connect()
        return self.client.fetch_message(messages, silent)

    def capabilities(self):
        logger.debug('capabilities')
        self._connect()
        return self.client.capabilities()
