# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase, skipUnless
from commonconf import settings, override_settings
from aws_message.message import Message
from aws_message.crypto import Signature, aes128cbc, CryptoException
import os

TEST_MESSAGES = [
    {'abc': 'def'},
    'abcdef 123456789',
    '[a, b, c]',
    'TopicArn: nope',
    ['a', 'b', 'c'],
]

TEST_MSG_SNS = {
    'SignatureVersion': '2',
    'Timestamp': '2018-08-22T04:00:56.843Z',
    'Signature': '...',
    'SigningCertURL': '',
    'MessageId': '11111111-0000-1111-2222-555555555555',
    'Message': (
        '{"EventID":"00000000-1111-2222-3333-444444444444","Href":'
        '"...","EventDate":"2018-08-21T21:00:56.832068-07:00","Previous":'
        '{"CurrentEnrollment":19,"Status":"open"},"Current":'
        '{"CurrentEnrollment":20,"Status":"closed"}}'),
    'UnsubscribeURL': '',
    'Type': 'Notification',
    'TopicArn': 'arn:aws:sns:us-east-1:111111111111:test-topic',
    'Subject': 'UW Event',
}

TEST_MSG_SNS_B64 = {
    'SignatureVersion': '1',
    'Timestamp': '2018-08-22T04:00:56.843Z',
    'Signature': '...',
    'SigningCertURL': '',
    'MessageId': '11111111-0000-1111-2222-555555555555',
    'Message': (
        'eyJFdmVudElEIjoiMDAwMDAwMDAtMTExMS0yMjIyLTMzMzMtNDQ0NDQ0NDQ0NDQ0'
        'IiwiSHJlZiI6Ii4uLiIsIkV2ZW50RGF0ZSI6IjIwMTgtMDgtMjFUMjE6MDA6NTYu'
        'ODMyMDY4LTA3OjAwIiwiUHJldmlvdXMiOnsiQ3VycmVudEVucm9sbG1lbnQiOjE5'
        'LCJTdGF0dXMiOiJvcGVuIn0sIkN1cnJlbnQiOnsiQ3VycmVudEVucm9sbG1lbnQi'
        'OjIwLCJTdGF0dXMiOiJjbG9zZWQifX0='),
    'UnsubscribeURL': '',
    'Type': 'Notification',
    'TopicArn': 'arn:aws:sns:us-east-1:111111111111:test-topic',
    'Subject': 'UW Event',
}


class TestMessageExtract(TestCase):
    @override_settings(AWS_SQS={'TEST': {}})
    def test_extract_inner_message_str(self):
        for msg in TEST_MESSAGES:
            message = Message(msg, settings.AWS_SQS['TEST'])
            body = message.extract()
            self.assertEqual(body, msg)

    @override_settings(AWS_SQS={'TEST': {}})
    def test_extract_inner_message_sns_base64(self):
        message = Message(TEST_MSG_SNS_B64, settings.AWS_SQS['TEST'])
        body = message.extract()

        self.assertEqual(
            body["EventID"], '00000000-1111-2222-3333-444444444444')
        self.assertEqual(body["Href"], '...')
        self.assertEqual(
            body["EventDate"], '2018-08-21T21:00:56.832068-07:00')

    @override_settings(AWS_SQS={'TEST': {}})
    def test_extract_inner_message_sns_json(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        body = message.extract()

        self.assertEqual(
            body["EventID"], '00000000-1111-2222-3333-444444444444')
        self.assertEqual(body["Href"], '...')
        self.assertEqual(
            body["EventDate"], '2018-08-21T21:00:56.832068-07:00')


class TestMessageValidate(TestCase):
    @override_settings(AWS_SQS={'TEST': {}})
    def test_validate(self):
        for msg in TEST_MESSAGES:
            message = Message(msg, settings.AWS_SQS['TEST'])
            self.assertEqual(message.validate(), True)

    @override_settings(AWS_SQS={'TEST': {
            'VALIDATE_SNS_SIGNATURE': False,
            'TOPIC_ARN': 'arn:aws:sns:us-east-1:111111111111:test-topic'}},)
    def test_validate_topic_arn(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        self.assertEqual(message.validate(), True)

    @override_settings(AWS_SQS={'TEST': {
            'VALIDATE_SNS_SIGNATURE': False,
            'TOPIC_ARN': 'arn:aws:sns:us-east-1:111111111111:wrong-topic'}},)
    def test_validate_topic_arn_diff(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        self.assertEqual(message.validate(), False)

    @override_settings(AWS_SQS={'TEST': {'VALIDATE_SNS_SIGNATURE': True}},
                       AWS_CA_BUNDLE='ca_certs.txt',
                       MEMCACHED_SERVERS=[("127.0.0.1", "11211")])
    @skipUnless(os.getenv("CACHE_TESTS"), "Set CACHE_TESTS=1 to run tests")
    def test_validate_message_invalid_signature(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        with self.assertRaises(CryptoException) as cm:
            message.validate()
        self.assertEqual(
            'Unknown SNS Signature Version: 2', str(cm.exception))

    @override_settings(AWS_SQS={'TEST': {'VALIDATE_SNS_SIGNATURE': True}},
                       AWS_CA_BUNDLE='ca_certs.txt',
                       MEMCACHED_SERVERS=[("127.0.0.1", "11211")])
    @skipUnless(os.getenv("CACHE_TESTS"), "Set CACHE_TESTS=1 to run tests")
    def test_validate_message_signature(self):
        message = Message(TEST_MSG_SNS_B64, settings.AWS_SQS['TEST'])
        with self.assertRaises(CryptoException) as cm:
            message.validate()
        self.assertEqual(
            'Cannot get certificate None: No host specified.',
            str(cm.exception))


class TestMessageDecrypt(TestCase):
    def test_decrypt_message(self):
        AES_KEY = 'DUMMY_KEY_FOR_TESTING_1234567890'
        AES_IV = 'DUMMY_IV_TESTING'

        aes = aes128cbc(AES_KEY, AES_IV)
        msg = aes.decrypt(b'1234567812345678')
        self.assertIsNotNone(msg)
