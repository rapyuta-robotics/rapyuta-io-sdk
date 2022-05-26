PROJECT_CREATE_SUCCESS = '''
{
    "ID": 1,
    "CreatedAt": "2020-10-06T05:28:02.435526602Z",
    "UpdatedAt": "2020-10-06T05:28:02.435526602Z",
    "DeletedAt": null,
    "name": "test-project",
    "guid": "project-guid",
    "users": [
        {
            "guid": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
            "firstName": "Test",
            "lastName": "User",
            "emailID": "example@example.com",
            "state":"ACTIVATED"
        }
    ],
    "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d"
}
'''

PROJECT_CREATE_INVITED_ORG_SUCCESS = '''
{
    "ID": 1,
    "CreatedAt": "2020-10-06T05:28:02.435526602Z",
    "UpdatedAt": "2020-10-06T05:28:02.435526602Z",
    "DeletedAt": null,
    "name": "test-project",
    "guid": "project-guid",
    "organization": {
        "guid": "invited-org-guid",
        "name": "test-org",
        "creator": "7f6f5a4b-f159-4992-a78f-1c8791addd3d"
    },
    "users": [
        {
            "guid": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
            "firstName": "Test",
            "lastName": "User",
            "emailID": "example@example.com",
            "state":"ACTIVATED"
        },
        {
            "guid": "7f6f5a4b-f159-4992-a78f-1c8791addd3d",
            "firstName": "Admin",
            "lastName": "User",
            "emailID": "admin@example.com",
            "state":"ACTIVATED"
        }
    ],
    "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d"
}
'''

PROJECT_GET_SUCCESS = '''
{
    "ID": 1,
    "CreatedAt": "2020-10-06T05:28:02.435526602Z",
    "UpdatedAt": "2020-10-06T05:28:02.435526602Z",
    "DeletedAt": null,
    "name": "test-project",
    "guid": "project-guid",
    "users": [
        {
            "guid": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
            "firstName": "Test",
            "lastName": "User",
            "emailID": "example@example.com",
            "state":"ACTIVATED"
        }
    ],
    "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d"
}
'''

PROJECT_LIST_SUCCESS = '''
[
    {
        "ID": 1,
        "CreatedAt": "2020-10-06T05:28:02.435526602Z",
        "UpdatedAt": "2020-10-06T05:28:02.435526602Z",
        "DeletedAt": null,
        "name": "test-project-1",
        "guid": "project-guid-1",
        "users": [
            {
                "guid": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
                "firstName": "Test",
                "lastName": "User",
                "emailID": "example@example.com",
                "state":"ACTIVATED"
            }
        ],
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
        "organization": {
        "ID": 10,
        "CreatedAt": "2020-10-06T05:28:02.435526602Z",
        "UpdatedAt": "2020-10-06T05:28:02.435526602Z",
        "DeletedAt": null,
        "guid": "org-wvnwcmvfkbajavjetttcutga",
        "name": "temp-org",
        "countryID": 103,
        "country": null,
        "province": "karnataka",
        "postalCode": "560030",
        "url": "www.google.com",
        "planID": 0,
        "state": "ACTIVATED",
        "users": null,
        "projects": null,
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
        "shortGUID": "kygsh"
      }
    },
    {
        "ID": 2,
        "CreatedAt": "2020-10-06T05:29:02.435526602Z",
        "UpdatedAt": "2020-10-06T05:29:02.435526602Z",
        "DeletedAt": null,
        "name": "test-project-2",
        "guid": "project-guid-2",
        "users": [
            {
                "guid": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
                "firstName": "Test",
                "lastName": "User",
                "emailID": "example@example.com",
                "state":"ACTIVATED"
            }
        ],
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
        "organization": {
        "ID": 10,
        "CreatedAt": "2020-10-06T05:28:02.435526602Z",
        "UpdatedAt": "2020-10-06T05:28:02.435526602Z",
        "DeletedAt": null,
        "guid": "org-wvnwcmvfkbajavjetttcutga",
        "name": "temp-org",
        "countryID": 103,
        "country": null,
        "province": "karnataka",
        "postalCode": "560030",
        "url": "www.google.com",
        "planID": 0,
        "state": "ACTIVATED",
        "users": null,
        "projects": null,
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d",
        "shortGUID": "kygsh"
      }
    }
]
'''
