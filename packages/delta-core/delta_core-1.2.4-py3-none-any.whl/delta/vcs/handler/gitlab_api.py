import requests
from typing import Any


class GitlabAPI:

    def __init__(self,
                 url: str,
                 private_token: str = '',
                 authorization_type='Bearer'):
        self._url = url
        self._private_token = private_token
        self._authorization_type = authorization_type

    def _get_requests(self, api_path: str):
        headers = {
            "Content-Type": "application/json",
            'Authorization':    f'{self._authorization_type} '
                                f'{self._private_token}'
        }
        return requests.get(
                    self._url + api_path,
                    headers=headers)

    def _post_requests(self, api_path: str, data):
        headers = {
            'Authorization':    f'{self._authorization_type} '
                                f'{self._private_token}'
        }
        return requests.post(
                        self._url + api_path,
                        headers=headers,
                        json=data)

    def _put_requests(self, api_path: str, data):
        headers = {
            "Content-Type": "application/json",
            'Authorization':    f'{self._authorization_type} '
                                f'{self._private_token}'
        }
        return requests.put(
                        self._url + api_path,
                        headers=headers,
                        json=data
                        )

    def _delete_request(self, api_path):
        headers = {
            'Authorization':    f'{self._authorization_type} '
                                f'{self._private_token}'
        }
        return requests.delete(
            self._url + api_path,
            headers=headers
        )

    def get_topics(self):
        return self._get_requests('/api/v4/topics')

    def get_topic_by_id(self, topic_id):
        return self._get_requests(f'/api/v4/topics/{topic_id}')

    def get_topic_by_name(self,
                          topic_name: str):
        res = self.get_topics()
        if res.status_code == 200:
            topics = res.json()
            for topic in topics:
                if topic["name"] == topic_name:
                    return topic
            return None

    def get_projects(self):
        return self._get_requests('/api/v4/projects')

    def get_namespace_id(self, namespace_full_path):
        response = self._get_requests('/api/v4/groups')
        if response.status_code == 200:
            content = response.json()
            for group in content:
                if (group['full_path'] == namespace_full_path):
                    return group['id']
        return None

    def get_projects_by_namespace_full_path(self, namespace_full_path):
        namespace_id = self.get_namespace_id(namespace_full_path)
        if namespace_id is not None:
            return self._get_requests('/api/v4/groups/'
                                      f'{namespace_id}/projects')
        return None

    def get_readme_of_project(self, project_id: int):
        return self._get_requests(f'/api/v4/projects/{project_id}/'
                                  'repository/files/README%2Emd/raw')

    def get_project_by_topic(self, topic_name):
        return self._get_requests(f'/api/v4/projects/?topic={topic_name}')

    def get_project_by_id(self, project_id: int):
        return self._get_requests(f'/api/v4/projects/{project_id}')

    def get_project_tags(self, project_id):
        return self._get_requests(f'/api/v4/projects/{project_id}'
                                  '/repository/tags')

    def create_topic(self,
                     name: str,
                     title: str,
                     description: str = '',
                     **kwargs):
        avatar = kwargs.get('avatar', None)
        print(f'Avatar {avatar} not used.')
        data = {
            "name": name,
            "title": title,
            "description": description
        }
        return self._post_requests('/api/v4/topics', data=data)

    def update_topic(self,
                     topic_id: int,
                     **kwargs):
        res = self.get_topic_by_id(topic_id)
        if res.status_code == 200:
            topic = res.json()
            topic['name'] = kwargs.get('name', topic['name'])
            topic['title'] = kwargs.get('title', topic['title'])
            topic['description'] = kwargs.get(
                                        'description',
                                        topic['description'])

            return self._put_requests(
                                f'/api/v4/topics/{topic_id}',
                                topic
                        )
        else:
            print(f'Update topic error : {res.status_code}')

    def add_topic_to_project(self, project_id, topic_name):
        res = self.get_project_by_id(project_id)
        if res.status_code == 200:
            project = res.json()
            project_topics = project['topics']
            project_topics.append(topic_name)
            data = {
                "topics": project_topics
            }
            return self._put_requests(f'/api/v4/projects/{project_id}', data)
        else:
            print(f"Add topic error : {res.status_code}")

    def remove_topic_to_project(self, project_id, topic_name):
        res = self.get_project_by_id(project_id)
        if res.status_code == 200:
            project = res.json()
            project['topics'].remove(topic_name)
            data = {
                'topics': project['topics']
            }
            return self._put_requests(f'/api/v4/projects/{project_id}', data)
        else:
            print(f"Remove topic error : {res.status_code}")

    def delete_topic(self, topic_id):
        res = self._delete_request(f'/api/v4/topics/{topic_id}')
        return res

    def download_project(self, project_id, sha):
        res = self._get_requests(f'/api/v4/projects/{project_id}/'
                                 f'repository/archive.zip?sha={sha}')
        return res

    def download_project_url(self, project_id, sha):
        return (f'{self._url}/api/v4/projects/{project_id}/'
                f'repository/archive.zip?sha={sha}')

    def close(self):
        pass

    def __enter__(self) -> "GitlabAPI":
        return self

    def __exit__(self, *args: Any, **kwargs) -> None:
        self.close()
