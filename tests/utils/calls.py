# encoding: utf-8
#  These calls are experimentally obtained.

from __future__ import absolute_import
from mock import call

CALL1 = call(None)
CALL2 = call(payload={'space_guid': 'space_guid', 'plan_id': u'test-plan', 'parameters': {'global': {'device_ids': []},
                                                                                          u'jakmybngjupwdjjdqztmcrjq': {
                                                                                              u'param2': u'value2',
                                                                                              u'param1': u'default_val'}},
                      'acceptance_incomplete': True, 'organization_guid': 'organization_guid', 'instance_id': 'default',
                      'service_id': 'my_package'})
CALL3 = call(payload={'space_guid': 'space_guid', 'plan_id': u'test-plan', 'parameters': {'global': {'device_ids': []},
                                                                                          u'jakmybngjupwdjjdqztmcrjq': {
                                                                                              u'param2': u'value2',
                                                                                              u'param1': u'default_val'}},
                      'acceptance_incomplete': True, 'organization_guid': 'organization_guid',
                      'instance_id': 'custom-deployment', 'service_id': 'my_package'})
CALL4 = call(payload={'space_guid': 'space_guid', 'plan_id': u'test-plan',
                      'parameters': {'global': {'device_ids': ['device-id-3']},
                                     u'jakmybngjupwdjjdqztmcrjq': {u'param2': u'value2', u'param1': u'default_val'}},
                      'acceptance_incomplete': True, 'organization_guid': 'organization_guid', 'instance_id': 'default',
                      'service_id': 'my_package'})
CALL5 = call(payload=None)
CALL6 = call(payload={'service_id': 'my_package', 'plan_id': u'test-plan'})
CALL7 = call(payload=None)
CALL8 = call(payload={'space_guid': 'space_guid', 'plan_id': u'test-plan', 'parameters': {'global': {'device_ids': []},
                                                                                          u'jakmybngjupwdjjdqztmcrjq': {
                                                                                              u'param2': u'value2',
                                                                                              u'param1': u'default_val'}},
                      'acceptance_incomplete': True, 'organization_guid': 'organization_guid', 'instance_id': 'default',
                      'service_id': 'my_package'})
CALL9 = call(payload={'space_guid': 'space_guid', 'plan_id': u'test-plan', 'parameters': {'global': {'device_ids': []},
                                                                                          u'jakmybngjupwdjjdqztmcrjq': {
                                                                                              u'param2': u'value2',
                                                                                              u'param1': u'default_val'}},
                      'acceptance_incomplete': True, 'organization_guid': 'organization_guid',
                      'instance_id': 'custom-deployment', 'context': {'dependentDeployments': ['my_deployment_id']},
                      'service_id': 'my_package'})
