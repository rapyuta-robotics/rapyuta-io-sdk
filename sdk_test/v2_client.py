from rapyuta_io.utils import prepend_bearer_to_auth_token, RestClient
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import get_api_response_data


class V2Client:
    """
        V2 Client used for sdk integration tests only. Its added here to avoid importing v2 client in cli.
        CLI have its own v2 client, it should not use sdk v2 client.

        :ivar auth_token: Auth Token
        :vartype guid: str
        :ivar v2_api_host: V2 Host URL
        :vartype name: str
    """

    def __init__(self, auth_token, v2_api_host):
        self.v2_api_host = v2_api_host
        self._auth_token = prepend_bearer_to_auth_token(auth_token)
        self._project = None

    def set_project(self, project):
        self._project = project

    def create_project(self, request):
        url = self.v2_api_host + '/v2/projects/'
        organization_guid = request['metadata']['organizationGUID']
        headers = dict(Authorization=self._auth_token, organizationguid=organization_guid)
        response = RestClient(url).method(HttpMethod.POST).headers(headers).execute(request)
        data = get_api_response_data(response, parse_full=True)
        return data.get('metadata')['guid']

    def delete_project(self, guid):
        url = self.v2_api_host + '/v2/projects/' + guid + '/'
        headers = dict(Authorization=self._auth_token)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        data = get_api_response_data(response, parse_full=True)
        return data
