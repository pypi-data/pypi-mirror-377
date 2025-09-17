import requests
from algosec_appviz import environment
from mydict import MyDict

regions = {
    'eu': 'eu.app.algosec.com',
    'us': 'us.app.algosec.com',
    'anz': 'anz.app.algosec.com',
    'me': 'me.app.algosec.com',
    'uae': 'uae.app.algosec.com',
    'ind': 'ind.app.algosec.com',
    'sgp': 'sgp.app.algosec.com'
}


class AppViz:
    def __init__(self, region='eu', tenant_id=None, client_id=None, client_secret=None, proxies=None):
        if region not in regions.keys():
            raise ValueError(f"Invalid region, must be one of: {', '.join(regions.keys())}")

        self.proxies = proxies

        login_url = f"https://{regions[region]}/api/algosaas/auth/v1/access-keys/login"
        data = {
            "tenantId": tenant_id or environment.get_tenant_id(),
            "clientId": client_id or environment.get_client_id(),
            "clientSecret": client_secret or environment.get_client_secret()
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(login_url, json=data, headers=headers, proxies=self.proxies)
        if response.status_code != 200:
            raise ConnectionError(f"Authentication to AppViz failed: {response.text}")

        self.url = 'https://' + regions[region]
        self._token_type = response.json()['token_type']
        self._token = response.json()['access_token']

    def create_application(self, name=None, **kwargs):
        if not name:
            raise ValueError("Name is required")

        body = {
            'name': name,
            **kwargs
        }

        result = self._make_api_call('POST',
                                     '/BusinessFlow/rest/v1/applications/new',
                                     body=body)

        return result

    def create_network_object(self, name=None, obj_type=None, content=None, **kwargs):
        valid_object_types = ['Range', 'Host', 'Group', 'Abstract']

        if not name:
            raise ValueError("Object name is required")
        if not obj_type:
            raise ValueError("Object type is required")
        if obj_type not in valid_object_types:
            raise ValueError(f"Object type invalid, allowed values: {', '.join(valid_object_types)}")

        body = {
            'name': name,
            'type': obj_type,
            'content': content,
            **kwargs
        }

        result = self._make_api_call('POST',
                                     '/BusinessFlow/rest/v1/network_objects/new',
                                     body=body)

        return result

    def delete_network_object(self, obj_id=None):
        """
        Deletes a network object in AppViz
        :param obj_id: The object ID
        :return: Change details if successful, empty string otherwise
        """
        if not obj_id:
            raise ValueError("Object ID is mandatory")

        result = self._make_api_call('DELETE',
                                     f'/BusinessFlow/rest/v1/network_objects/{obj_id}')

        if result['httpStatusCode'] != 200:
            print(f"Error deleting object: {result['message']}")
            return ""

        return result

    def update_network_object(self, obj_id=None, **kwargs):
        """
        Updates a network object in AppViz
        :return: The new object details, if successful, empty string otherwise
        """
        if not obj_id:
            raise ValueError("Object ID is mandatory")

        result = self._make_api_call('POST',
                                     f'/BusinessFlow/rest/v1/network_objects/{obj_id}',
                                     body={**kwargs})

        if isinstance(result, dict) and 'networkObject' in result.keys():
            return result['networkObject']

        try:
            print(result[1])
        except KeyError:
            if 'success' in result.keys() and not result['success']:
                print(result['message'])

        return ""

    def get_applications(self):
        response = self._make_api_call('GET',
                                       '/BusinessFlow/rest/v1/applications')

        return [MyDict(x) for x in response]

    def get_all_network_objects(self):
        """
        Gets all the network objects from AppViz. This could take some time, depending on the number of objects.
        :return: The list of objects
        """
        appviz_objects = []
        page = 1

        while True:
            print(f"Getting AppViz Network Objects, page {page}...")
            objects = self.list_network_objects(page_number=page)
            page = page + 1
            appviz_objects.extend(objects)
            if len(objects) < 1000:
                break

        return appviz_objects

    def list_network_objects(self, page_number=1, page_size=1000):
        """
        Get a list of objects based on the page_size (the number of objects to be retrieved) and the page number
        :param page_number: Page number, defaults to 1
        :param page_size: Page size, defaults to 1000
        :return: The list of objects
        """
        response = self._make_api_call('GET',
                                       '/BusinessFlow/rest/v1/network_objects/',
                                       params={'page_number': page_number, 'page_size': page_size})

        return [MyDict(x) for x in response]

    def search_exact_object(self, content):
        response = self._make_api_call('GET',
                                       '/BusinessFlow/rest/v1/network_objects/find',
                                       params={'address': content, 'type': 'EXACT'})

        return [MyDict(x) for x in response]

    def _make_api_call(self, method, url_path, body=None, params=None):
        valid_methods = ['get', 'post', 'delete']
        headers = {
            'Accept': 'application/json',
            'Authorization': f'{self._token_type} {self._token}'
        }

        url = self.url + url_path

        if method.lower() == 'get':
            response = requests.get(url, headers=headers, json=body, params=params, proxies=self.proxies)
        elif method.lower() == 'post':
            response = requests.post(url, headers=headers, json=body, params=params, proxies=self.proxies)
        elif method.lower() == 'delete':
            response = requests.delete(url, headers=headers, json=body, params=params, proxies=self.proxies)
        else:
            raise ValueError(f"Invalid method, must be: {', '.join(valid_methods)}")

        return response.json()
