USER_GROUP_LIST_SUCCESS = '''
[
    {
        "guid": "group-kyqnkgdjfojwnsstggappfdq",
        "name": "new_group",
        "description": "test",
        "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
        "members": [
            {
                "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
                "firstName": "Qa",
                "lastName": "Rapyuta",
                "emailID": "qa.rapyuta+e2e@gmail.com",
                "state": "ACTIVATED",
                "organizations": null
            }
        ],
        "admins": [
            {
                "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
                "firstName": "Qa",
                "lastName": "Rapyuta",
                "emailID": "qa.rapyuta+e2e@gmail.com",
                "state": "ACTIVATED",
                "organizations": null
            }
        ],
        "projects": [
            {
                "ID": 45,
                "CreatedAt": "2020-07-20T12:55:31.280953Z",
                "UpdatedAt": "2023-04-20T05:14:16.278633Z",
                "DeletedAt": "2023-06-05T13:53:26.612222Z",
                "name": "1yb",
                "guid": "project-ewhoogxxkjkyklilowpaqlid",
                "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
            },
            {
                "ID": 836,
                "CreatedAt": "2023-04-20T05:07:44.901605Z",
                "UpdatedAt": "2023-04-20T05:14:16.281498Z",
                "DeletedAt": "2023-06-05T13:55:27.152667Z",
                "name": "test-1",
                "guid": "project-gmlkoiktloumndxkdhixnaiw",
                "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
            },
            {
                "ID": 837,
                "CreatedAt": "2023-04-20T05:14:13.678163Z",
                "UpdatedAt": "2023-04-20T05:14:16.284306Z",
                "DeletedAt": "2023-06-05T13:54:11.790783Z",
                "name": "test-2",
                "guid": "project-qbohzesewiobwgmesknvtwge",
                "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
            },
            {
                "ID": 850,
                "CreatedAt": "2023-06-02T13:52:23.766722Z",
                "UpdatedAt": "2023-06-02T13:52:23.766722Z",
                "DeletedAt": "2023-06-05T13:54:14.783998Z",
                "name": "review",
                "guid": "project-chsv85sjpuuhrd00vf50",
                "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
            }
        ],
        "update": {
            "members": {},
            "admins": {},
            "projects": {}
        }
    },
    {
        "guid": "group-dcqsyqclnpxwcgboilolbdid",
        "name": "swagnik_test_group",
        "description": "testing for user groups feature in sdk and cli",
        "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
        "members": [
            {
                "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
                "firstName": "Qa",
                "lastName": "Rapyuta",
                "emailID": "qa.rapyuta+e2e@gmail.com",
                "state": "ACTIVATED",
                "organizations": null
            }
        ],
        "admins": [
            {
                "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
                "firstName": "Qa",
                "lastName": "Rapyuta",
                "emailID": "qa.rapyuta+e2e@gmail.com",
                "state": "ACTIVATED",
                "organizations": null
            }
        ],
        "projects": [
            {
                "ID": 851,
                "CreatedAt": "2023-06-05T14:58:20.832424Z",
                "UpdatedAt": "2023-06-26T13:59:32.806651Z",
                "DeletedAt": null,
                "name": "swagnik",
                "guid": "project-chuvg34jpuuhrd00vf5g",
                "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
            }
        ],
        "update": {
            "members": {},
            "admins": {},
            "projects": {}
        }
    }
]
'''

USER_GROUP_GET_SUCCESS = '''
{
    "guid": "group-dcqsyqclnpxwcgboilolbdid",
    "name": "swagnik_test_group",
    "description": "testing for user groups feature in sdk and cli",
    "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
    "members": [
        {
            "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
            "firstName": "Qa",
            "lastName": "Rapyuta",
            "emailID": "qa.rapyuta+e2e@gmail.com",
            "state": "ACTIVATED",
            "organizations": null
        }
    ],
    "admins": [
        {
            "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
            "firstName": "Qa",
            "lastName": "Rapyuta",
            "emailID": "qa.rapyuta+e2e@gmail.com",
            "state": "ACTIVATED",
            "organizations": null
        }
    ],
    "projects": [
        {
            "ID": 851,
            "CreatedAt": "2023-06-05T14:58:20.832424Z",
            "UpdatedAt": "2023-06-26T13:59:32.806651Z",
            "DeletedAt": null,
            "name": "swagnik",
            "guid": "project-chuvg34jpuuhrd00vf5g",
            "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
        }
    ],
    "update": {
        "members": {},
        "admins": {},
        "projects": {}
    }
}
'''

USER_GROUP_DELETE_SUCCESS = '''
{
    "success": true,
    "error": ""
}
'''

USER_GROUP_DELETE_FAILURE = '''
{
    "success": false,
    "error": "group group-owajeznkoqrhtwdrgwgxkywp not found"
}
'''

USER_GROUP_CREATE_SUCCESS = '''
{
    "guid": "group-gtvegbkbsikwsfrrckcvtjdg",
    "name": "test-random",
    "description": "test description",
    "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
    "members": [
        {
            "guid": "213215e9-fec2-4fd1-b809-e447f22f3676",
            "firstName": "Pallab",
            "lastName": "Pain",
            "emailID": "pallab.pain+new01@rapyuta-robotics.com",
            "state": "ACTIVATED",
            "organizations": null
        },
        {
            "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
            "firstName": "Qa",
            "lastName": "Rapyuta",
            "emailID": "qa.rapyuta+e2e@gmail.com",
            "state": "ACTIVATED",
            "organizations": null
        }
    ],
    "admins": [
        {
            "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
            "firstName": "Qa",
            "lastName": "Rapyuta",
            "emailID": "qa.rapyuta+e2e@gmail.com",
            "state": "ACTIVATED",
            "organizations": null
        }
    ],
    "projects": [
        {
            "ID": 851,
            "CreatedAt": "2023-06-05T14:58:20.832424Z",
            "UpdatedAt": "2023-07-03T14:35:36.981069299Z",
            "DeletedAt": null,
            "name": "swagnik",
            "guid": "project-chuvg34jpuuhrd00vf5g",
            "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
        }
    ],
    "organization": {
        "ID": 13,
        "CreatedAt": "2020-07-14T09:44:42.737203Z",
        "UpdatedAt": "2023-07-03T14:35:36.968238557Z",
        "DeletedAt": null,
        "guid": "org-bqgpmsafgnvnawlkuvxtxohs",
        "name": "e2e-testing",
        "countryID": 103,
        "country": {
            "ID": 103,
            "CreatedAt": "2020-06-05T12:11:33.031097Z",
            "UpdatedAt": "2023-07-03T14:35:36.966772306Z",
            "DeletedAt": null,
            "name": "India",
            "code": "IN"
        },
        "province": "Bangalore",
        "postalCode": "560068",
        "url": "www.e2etesting.com",
        "planID": 0,
        "state": "ACTIVATED",
        "users": null,
        "projects": null,
        "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
        "shortGUID": "anvgv"
    },
    "update": {
        "members": {},
        "admins": {},
        "projects": {}
    }
}
'''

USER_GROUP_UPDATE_SUCCESS = '''
{
    "guid": "group-wmvxbcavohpqusdhbakhgpuv",
    "name": "test-usergroup",
    "description": "Sample user group",
    "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
    "members": [
        {
            "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
            "firstName": "Qa",
            "lastName": "Rapyuta",
            "emailID": "qa.rapyuta+e2e@gmail.com",
            "state": "ACTIVATED",
            "organizations": null
        }
    ],
    "admins": [
        {
            "guid": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
            "firstName": "Qa",
            "lastName": "Rapyuta",
            "emailID": "qa.rapyuta+e2e@gmail.com",
            "state": "ACTIVATED",
            "organizations": null
        }
    ],
    "projects": [
        {
            "ID": 851,
            "CreatedAt": "2023-06-05T14:58:20.832424Z",
            "UpdatedAt": "2023-07-04T17:22:48.100317912Z",
            "DeletedAt": null,
            "name": "swagnik",
            "guid": "project-chuvg34jpuuhrd00vf5g",
            "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582"
        }
    ],
    "organization": {
        "ID": 13,
        "CreatedAt": "2020-07-14T09:44:42.737203Z",
        "UpdatedAt": "2023-07-04T17:22:48.089828668Z",
        "DeletedAt": null,
        "guid": "org-bqgpmsafgnvnawlkuvxtxohs",
        "name": "e2e-testing",
        "countryID": 103,
        "country": {
            "ID": 103,
            "CreatedAt": "2020-06-05T12:11:33.031097Z",
            "UpdatedAt": "2023-07-04T17:22:48.08836342Z",
            "DeletedAt": null,
            "name": "India",
            "code": "IN"
        },
        "province": "Bangalore",
        "postalCode": "560068",
        "url": "www.e2etesting.com",
        "planID": 0,
        "state": "ACTIVATED",
        "users": null,
        "projects": null,
        "creator": "6e36a251-aeeb-4b0b-bc26-bec7adc1c582",
        "shortGUID": "anvgv"
    },
    "update": {
        "members": {},
        "admins": {},
        "projects": {}
    }
}
'''