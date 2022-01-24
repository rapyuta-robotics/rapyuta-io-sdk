# encoding: utf-8
from __future__ import absolute_import
import unittest

from rapyuta_io.utils.error import OperationNotAllowedError
from rapyuta_io.utils.objdict import ObjDict, ImmutableKeyDict, to_objdict, to_dict


# TODO setattr and delattr cannot be further tested without weird hacks.

class ObjDictTests(unittest.TestCase):

    def test_objdict_conversions(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        objdict = to_objdict(test_in)
        test_out = to_dict(objdict)
        self.assertEqual(test_in, test_out)

        test_out2 = objdict.to_dict()
        self.assertEqual(test_out2, test_out)

        objdict2 = ObjDict.from_dict(test_in)
        self.assertEqual(objdict2, objdict)

        objdict3 = objdict.from_dict(test_in)
        self.assertEqual(objdict3, objdict)

    def test_objdict_conversions_list(self):
        test_in = [1, 2, [3.1, 3.2]]
        objdict = to_objdict(test_in)
        test_out = to_dict(objdict)
        self.assertEqual(test_in, test_out)

    def objdict_conversions_tuple(self):
        test_in = (1, 'two', [3.0, 4.0, ], ('five', 6))
        objdict = to_objdict(test_in)
        test_out = to_dict(objdict)
        self.assertEqual(test_in, test_out)

    def test_objdict_immutable_dict_ok(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        test_dict = ImmutableKeyDict(to_objdict(test_in))
        test_dict['key1'] = 'new_value1'
        self.assertEqual(test_dict['key1'], 'new_value1')
        test_dict['device_id'] = 'my_device'
        self.assertEqual(test_dict['device_id'], 'my_device')

    def test_objdict_immutable_dict_wrong(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        test_dict = ImmutableKeyDict(to_objdict(test_in))
        with self.assertRaises(OperationNotAllowedError):
            test_dict['test-key'] = 'test-val'

    def test_objdict_immutable_dict_del(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        test_dict = ImmutableKeyDict(to_objdict(test_in))
        with self.assertRaises(OperationNotAllowedError):
            del test_dict['key1']

    def test_objdict_contains(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        objdict = to_objdict(test_in)
        self.assertTrue('key3' in objdict)
        self.assertFalse('subkey1' in objdict)

    def test_objdict_delattr(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        objdict = to_objdict(test_in)
        del objdict.key1
        self.assertFalse('key1' in objdict)

    def test_objdict_delattr(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        objdict = to_objdict(test_in)
        with self.assertRaises(AttributeError):
            del objdict.key1
            del objdict.key1

    def test_objdict_immutable_dict_error1(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        test_dict = ImmutableKeyDict(to_objdict(test_in))
        with self.assertRaises(OperationNotAllowedError):
            setattr(test_dict, 'key4', 'new_value4')

    def test_objdict_immutable_dict_error2(self):
        test_in = {'key1': 'value1', 'key2': 2.0, 'key3': {'subkey1': 'subval1', 'subkey2': 1.2}}
        test_dict = ImmutableKeyDict(to_objdict(test_in))
        with self.assertRaises(OperationNotAllowedError):
            delattr(test_dict, 'key1')
