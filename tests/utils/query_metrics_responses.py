QUERY_METRICS_SUCCESS = '''
{
    "response": {
        "data": {
            "columns": [
                {
                    "name": "timestamp"
                },
                {
                    "function": "count",
                    "metric_group": "cpu",
                    "name": "usage_user",
                    "tag_names": [],
                    "tag_values": []
                }
            ],
            "rows": [
                [
                    1612814880000000000,
                    1612814890000000000

                ],
                [
                    0.7716360673079268,
                    0.7716360673079268
                ]
            ]
        }
    }
}
'''

QUERY_METRICS_SUCCESS_WITH_GROUPBY = '''
{
    "response": {
        "data": {
            "columns": [
                {
                    "name": "timestamp"
                },
                {
                    "function": "count",
                    "metric_group": "cpu",
                    "name": "usage_idle",
                    "tag_names": [
                        "device_id",
                        "host"
                    ],
                    "tag_values": [
                        "35b1a367-5c83-473e-9e44-1e57ac520c44",
                        "rapyuta"
                    ]
                },
                {
                    "function": "count",
                    "metric_group": "cpu",
                    "name": "usage_idle",
                    "tag_names": [
                        "device_id",
                        "host"
                    ],
                    "tag_values": [
                        "7d4283a4-5912-4f85-83d3-f6e6584f36dc",
                        "rapyuta"
                    ]
                }
            ],
            "rows": [
                [
                    1612814880000000000,
                    1612814890000000000,
                    1612814900000000000,
                    1612814910000000000
                ],
                [
                    0.5106911720333912,
                    null,
                    null,
                    0.35028308953010395
                ],
                [
                    0.9757220882033476,
                    null,
                    null,
                    null
                ]
            ]
        }
    }
}

'''

LIST_METRICS_SUCCESS = '''
{
    "response": {
        "data": {
            "metrics": [
                {
                    "metric_group": "cpu",
                    "metric_names": [
                        "usage_guest",
                        "usage_guest_nice",
                        "usage_idle",
                        "usage_iowait",
                        "usage_irq",
                        "usage_nice",
                        "usage_softirq",
                        "usage_steal",
                        "usage_system",
                        "usage_user"
                    ]
                }
            ]
        }
    }
}
'''

LIST_TAG_KEYS_SUCCESS = '''
{
    "response": {
        "data": {
            "tag_keys": [
                {
                    "metric_group": "cpu",
                    "tags": [
                        "cpu",
                        "device_id",
                        "host",
                        "tenant_id"
                    ]
                }
            ]
        }
    }
}
'''

LIST_TAG_VALUES_SUCCESS = '''
{
    "response": {
        "data": {
            "tags_values": [
                "cpu-total",
                "cpu0",
                "cpu1",
                "cpu2",
                "cpu3"
            ]
        }
    }
}
'''