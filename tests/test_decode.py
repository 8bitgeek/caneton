# -*- coding: utf-8 -*-
# Copyright © 2015 Polyconseil SAS
# SPDX-License-Identifier: BSD-3-Clause
#

from unittest import TestCase
import binascii
import json

import caneton


class TestDecode(TestCase):

    def test_signal_with_empty_value(self):
        signal_info = {
            'bit_start': 32,
            'length': 16,
            'little_endian': 1,
        }
        message_binary_lsb = '0000000010101111000000001010001100000000'
        # message_binary_msb is not required (LSB)
        with self.assertRaises(caneton.DecodingError) as cm:
            caneton.signal_decode(
                "Foo", signal_info, None, message_binary_lsb, len(message_binary_lsb))
        exception = cm.exception
        self.assertEqual(
            str(exception),
            "The string value extracted for signal 'Foo' is empty [-8:8].")

    def test_message(self):
        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message_data = binascii.unhexlify('01780178010000')
        message = caneton.message_decode(
            message_id=0x701, message_length=len(message_data),
            message_data=message_data, dbc_json=dbc_json)
        signal = caneton.message_get_signal(message, 'Bar2')
        self.assertEqual(signal['name'], 'Bar2')
        self.assertEqual(signal['value'], 188.0)
        self.assertEqual(signal['unit'], 'V')

        message_data = binascii.unhexlify('041d000000000000')
        message = caneton.message_decode(
            message_id=0x63f,
            message_length=len(message_data),
            message_data=message_data,
            dbc_json=dbc_json,
        )
        signal = caneton.message_get_signal(message, 'TempsChargeRestant')
        self.assertIsNotNone(signal)
        self.assertEqual(signal['value'], 29)
        self.assertEqual(signal['unit'], 'mn')

        message_data = binascii.unhexlify('00CDCCA042030000')
        message = caneton.message_decode(
            message_id=0x63f,
            message_length=len(message_data),
            message_data=message_data,
            dbc_json=dbc_json,
        )
        signal = caneton.message_get_signal(message, 'Temperature_max')
        self.assertIsNotNone(signal)
        self.assertEqual(signal['value'], 1117834445)
        self.assertEqual(signal['unit'], u'°C')

        signal = caneton.message_get_signal(message, 'PuissanceDispoVch')
        self.assertIsNotNone(signal)
        self.assertEqual(signal['value'], 1)
        self.assertEqual(signal['unit'], '')

        signal = caneton.message_get_signal(message, 'PuissanceDispoVpack')
        self.assertIsNotNone(signal)
        self.assertEqual(signal['value'], 1)
        self.assertEqual(signal['unit'], '')

    def test_message_wo_signals(self):
        message_id = 542
        message_length = 8
        message_data = b' ' * message_length

        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message = caneton.message_decode(
            message_id=message_id, message_length=message_length,
            message_data=message_data, dbc_json=dbc_json)
        self.assertEqual(message['signals'], [])
        self.assertEqual(
            caneton.message_get_signal(message, 'Doesntexist'), None)

    def test_message_with_float_type(self):
        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message_data = binascii.unhexlify('0000284200000000')
        message = caneton.message_decode(
            message_id=0x63e, message_length=len(message_data),
            message_data=message_data, dbc_json=dbc_json,
        )
        signal = caneton.message_get_signal(message, 'HvBatteryCurrent_Puissance')
        self.assertEqual(signal['name'], 'HvBatteryCurrent_Puissance')
        self.assertEqual(signal['value'], 42.0)
        self.assertEqual(signal['unit'], 'A')

    def test_message_with_double_type(self):
        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message_data = binascii.unhexlify('0000000000004540')
        message = caneton.message_decode(
            message_id=0x63e, message_length=len(message_data),
            message_data=message_data, dbc_json=dbc_json,
        )
        signal = caneton.message_get_signal(message, 'HvBatteryCurrent_PuissanceDouble')
        self.assertEqual(signal['name'], 'HvBatteryCurrent_PuissanceDouble')
        self.assertEqual(signal['value'], 42.0)
        self.assertEqual(signal['unit'], 'A')

    def test_message_with_positive_signed_int_type(self):
        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message_data = binascii.unhexlify('1100E80300000000')
        message = caneton.message_decode(
            message_id=0x195, message_length=len(message_data),
            message_data=message_data, dbc_json=dbc_json,
        )
        signal = caneton.message_get_signal(message, 'truck_speed')
        self.assertEqual(signal['name'], 'truck_speed')
        self.assertEqual(signal['value'], 10.0)
        self.assertEqual(signal['unit'], 'km/h')

    def test_message_with_negative_signed_int_type(self):
        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message_data = binascii.unhexlify('1100F9FB00000000')
        message = caneton.message_decode(
            message_id=0x195, message_length=len(message_data),
            message_data=message_data, dbc_json=dbc_json,
        )
        signal = caneton.message_get_signal(message, 'truck_speed')
        self.assertEqual(signal['name'], 'truck_speed')
        self.assertEqual(signal['value'], -10.31)
        self.assertEqual(signal['unit'], 'km/h')

    def test_signal_decode_return_type(self):
        with open('./tests/dbc.json', 'r') as f:
            dbc_json = json.loads(f.read())

        message_data = b'\xff\xff\xff\xff\xff\xff\xff\xff'
        message = caneton.message_decode(
            message_id=1942, message_length=len(message_data),
            message_data=message_data, dbc_json=dbc_json,
        )

        # Factor is float and integer
        signal = caneton.message_get_signal(message, 'Foo1')
        self.assertEqual(signal['value'], 255)
        self.assertIs(type(signal['value']), int)

        # Offset is float and integer
        signal = caneton.message_get_signal(message, 'Foo2')
        self.assertEqual(signal['value'], 255)
        self.assertIs(type(signal['value']), int)

        # Factor is float but not integer
        signal = caneton.message_get_signal(message, 'Bar1')
        self.assertEqual(signal['value'], 32767.5)
        self.assertIs(type(signal['value']), float)

        # Offset is float but not integer
        signal = caneton.message_get_signal(message, 'Bar2')
        self.assertEqual(signal['value'], 65535.5)
        self.assertIs(type(signal['value']), float)
