# encoding: utf-8
# These paylaods are experimentally obtained. We do not use the
# query_builder.build_device_selection_payload in purpose, as that might
# cover errors.

PAYLOAD1 = {
    'selection_criteria': [
        {
            'measurements': {
                'select_criteria': {
                    'fields': [
                        {
                            'operator': '>',
                            'field': 'value',
                            'values': {
                                'max_value': '20',
                                'min_value': 100
                            }
                        }
                    ],
                    'clause': 'OR'
                },
                'measurement': 'battery'
            }
        }
    ],
    'clause': 'AND'
}

PAYLOAD2 = {
    'selection_criteria': [
        {
            'labels': {
                'select_criteria': {
                    'fields': [
                        {
                            'operator': '=',
                            'field': 'test_label',
                            'values': {
                                'max_value': 'true',
                                'min_value': ''
                            }
                        }
                    ],
                    'clause': 'OR'
                }
            }
        }
    ],
    'clause': 'AND'
}
