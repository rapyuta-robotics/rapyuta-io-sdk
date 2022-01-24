from __future__ import absolute_import
import unittest

import enum

from rapyuta_io.utils.object_converter import ObjBase, nested_field, enum_field, list_field


class SampleConverterClass(ObjBase):
    def get_deserialize_map(self):
        return {
            'string_key': 'stringKey',
        }

    def get_serialize_map(self):
        return {
            'stringKey': 'string_key',
        }


class SampleEnumClass(str, enum.Enum):
    val = 'VAL'


class NonObjBaseClass:
    def __init__(self):
        pass


class SampleConverterBase(ObjBase):
    def get_deserialize_map(self):
        return {
            'string_key': 'stringKey',
            'int_key': 'intKey',
            'list_key': 'listKey',
            'bool_key': 'boolKey',
            'nested_key': nested_field('nestedKey', SampleConverterClass),
            'list_nested_key': list_field('listNestKey', SampleConverterClass),
            'enum_key': enum_field('enumKey', SampleEnumClass)
        }

    def get_serialize_map(self):
        return {
            'stringKey': 'string_key',
            'intKey': 'int_key',
            'listKey': 'list_key',
            'boolKey': 'bool_key',
            'nestedKey': 'nested_key',
            'listNestKey': 'list_nested_key',
            'enumKey': 'enum_key'
        }


class ObjBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.string_val = 'stringVal'
        self.int_val = 123
        self.bool_val = False
        self.list_val = ['listVal1']
        self.nested_val = {'stringKey': self.string_val}
        self.base_data = {'stringKey': self.string_val, 'intKey': self.int_val, 'listKey': self.list_val,
                          'nestedKey': self.nested_val, 'listNestKey': [self.nested_val],
                          'enumKey': 'VAL', 'boolKey': self.bool_val}
        self.nested_obj = self.create_nested_obj()
        self.base_obj = self.create_base_obj()

    def create_nested_obj(self):
        o = SampleConverterClass()
        o.string_key = self.string_val
        return o

    def create_base_obj(self):
        o = SampleConverterBase()
        o.string_key = self.string_val
        o.int_key = self.int_val
        o.bool_key = self.bool_val
        o.list_key = self.list_val
        o.nested_key = self.nested_obj
        o.list_nested_key = [self.nested_obj]
        o.enum_key = SampleEnumClass.val
        return o

    def test_deserialize(self):
        obj = SampleConverterBase.deserialize(self.base_data)
        self.assertEqual(obj.string_key, self.string_val)
        self.assertEqual(obj.int_key, self.int_val)
        self.assertEqual(obj.bool_key, self.bool_val)
        self.assertEqual(obj.list_key, self.list_val)
        self.assertEqual(obj.nested_key.serialize(), self.nested_val)
        self.assertEqual([o.serialize() for o in obj.list_nested_key], [self.nested_val])
        self.assertEqual(obj.enum_key, SampleEnumClass.val)

    def test_deserialize_with_only(self):
        obj = SampleConverterBase.deserialize(self.base_data)
        self.base_data['stringKey'] = 'newStringVal'
        self.base_data['intKey'] = 456
        SampleConverterBase.deserialize(self.base_data, obj=obj, only=['string_key'])
        self.assertEqual(obj.int_key, self.int_val)
        self.assertEqual(obj.string_key, 'newStringVal')

    def test_serialize(self):
        data = self.base_obj.serialize()
        self.assertEqual(data, self.base_data)

    def test_nested_with_non_obj_base_subclass(self):
        with self.assertRaises(Exception) as e:
            nested_field('api_field', NonObjBaseClass)

        self.assertEqual(str(e.exception), 'NonObjBaseClass should be a subclass of ObjBase')

    def test_nested_list_with_non_obj_base_subclass(self):
        with self.assertRaises(Exception) as e:
            list_field('api_field', NonObjBaseClass)

        self.assertEqual(str(e.exception), 'NonObjBaseClass should be a subclass of ObjBase')

    def test_enum_with_non_enum_subclass(self):
        with self.assertRaises(Exception) as e:
            enum_field('api_field', NonObjBaseClass)
        self.assertEqual(str(e.exception), 'NonObjBaseClass should be a subclass of Enum')

    def test_deserialize_only_not_list(self):
        with self.assertRaises(Exception) as e:
            SampleConverterBase.deserialize(self.base_data, only='invalid')
        self.assertEqual(str(e.exception), 'only should be a list of string')

    def test_deserialize_only_not_list_of_string(self):
        with self.assertRaises(Exception) as e:
            SampleConverterBase.deserialize(self.base_data, only=['api_field', True])
        self.assertEqual(str(e.exception), 'only should be a list of string')
