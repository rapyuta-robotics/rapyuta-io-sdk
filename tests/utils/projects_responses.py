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
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d"
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
        "creator": "6f6f5a4b-f159-4992-a78f-1c8791addd3d"
    }
]
'''
