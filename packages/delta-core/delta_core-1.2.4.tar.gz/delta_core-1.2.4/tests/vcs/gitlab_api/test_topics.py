import unittest
from unittest import mock
from delta.vcs.handler import GitlabAPI


class TestUpdateMethod(unittest.TestCase):
    @mock.patch("delta.vcs.handler.gitlab_api.requests.put")
    @mock.patch("delta.vcs.handler.gitlab_api.requests.get")
    def test_with_wrong_token(self,
                              request_mock_get,
                              request_mock_put):
        request_mock_get.return_value = mock.Mock(
            status_code=200,
            json=lambda: {"id": 1,
                          "name": "starter-kit",
                          "description": "starter",
                          "title": "starter-kit"}
        )

        request_mock_put.return_value = mock.Mock(
            status_code=401,
            json=lambda: {
                "401": "Not authorized"
            }
        )
        glapi = GitlabAPI('https://git.gael.fr', 'token')

        res = glapi.update_topic(
                1, description="starter kit"
            )
        self.assertEqual(
            res.status_code, 401)

    @mock.patch('delta.vcs.handler.gitlab_api.requests.get')
    def test_with_topic_id_dont_exist(self,
                                      request_mock):
        request_mock.return_value = mock.Mock(
                        status_code=401,
                        json=lambda: {
                            "401": "Not authorized"
                        })
        glapi = GitlabAPI('https://git.gael.fr', 'token')
        self.assertIsNone(glapi.update_topic(-1, description="starter kit"))


class TestAddMethod(unittest.TestCase):
    @mock.patch("delta.vcs.handler.gitlab_api.requests.get")
    def test_with_wrong_token_and_wrong_id(self,
                                           request_mock):
        request_mock.return_value = mock.Mock(
                        status_code=401,
                        json=lambda: {
                            "401": "Not authorized"
                        })
        glapi = GitlabAPI('https://git.gael.fr', 'token')

        self.assertIsNone(glapi.add_topic_to_project(-1, "starter-kit"))

    @mock.patch("delta.vcs.handler.gitlab_api.requests.put")
    @mock.patch("delta.vcs.handler.gitlab_api.requests.get")
    def test_add_with_wrong_token(self,
                                  request_mock_get,
                                  request_mock_put):
        request_mock_get.return_value = mock.Mock(
                        status_code=200,
                        json=lambda: {"id": 1,
                                      "topics": ['test']})

        request_mock_put.return_value = mock.Mock(
                        status_code=401,
                        json=lambda: {
                            "401": "Not authorized"
                        })

        glapi = GitlabAPI('https://git.gael.fr', 'token')

        self.assertEqual(
            glapi.add_topic_to_project(
                1,
                "starter-kit"
            ).status_code, 401)


class TestGetMethods(unittest.TestCase):
    @mock.patch("delta.vcs.handler.gitlab_api.requests.get")
    def test_get_topic_by_name_not_in_list(self,
                                           request_mock):
        request_mock.return_value = mock.Mock(status_code=200,
                                              json=lambda: [
                                                    {
                                                        "id": 1,
                                                        "name": "test"
                                                    },
                                                    {
                                                        "id": 2,
                                                        "name": "toto"
                                                    }])

        glapi = GitlabAPI('https://git.gael.fr', 'token')
        self.assertIsNone(glapi.get_topic_by_name('toti'))

    @mock.patch("delta.vcs.handler.gitlab_api.requests.get")
    def test_get_topic_by_name_in_list(self,
                                       request_mock):
        request_mock.return_value = mock.Mock(status_code=200,
                                              json=lambda: [
                                                    {
                                                        "id": 1,
                                                        "name": "test"
                                                    },
                                                    {
                                                        "id": 2,
                                                        "name": "toto"
                                                    }])

        glapi = GitlabAPI('https://git.gael.fr', 'token')
        self.assertIsNotNone(glapi.get_topic_by_name('toto'))
        self.assertEqual(
            glapi.get_topic_by_name('toto'),
            {"id": 2, "name": "toto"}
        )

    @mock.patch('delta.vcs.handler.gitlab_api.requests.get')
    def test_get_topics_with_wrong_token(self,
                                         request_mock):
        request_mock.return_value = mock.Mock(status_code=200,
                                              json=lambda: {
                                                  "topics": [
                                                    {
                                                        "id": 1,
                                                        "name": "test"
                                                    },
                                                    {
                                                        "id": 2,
                                                        "name": "toto"
                                                    }]})

        glapi = GitlabAPI('https://git.gael.fr', 'token')
        self.assertEqual(glapi.get_topics().status_code, 200)


class TestCreateMethod(unittest.TestCase):
    @mock.patch('delta.vcs.handler.gitlab_api.requests.post')
    @mock.patch('delta.vcs.handler.gitlab_api.requests.get')
    def test_create_topic_with_wrong_token(self,
                                           request_mock_get,
                                           request_mock_post):
        request_mock_get.return_value = mock.Mock(status_code=401,
                                                  json=lambda: {
                                                      "401": "Not authorized"
                                                    })
        request_mock_post.return_value = mock.Mock(
                        status_code=401,
                        json=lambda: {
                            "401": "Not authorized"
                        })
        glapi = GitlabAPI('https://git.gael.fr', 'token')
        self.assertEqual(glapi.create_topic('hurricane',
                                            'hurricane'
                                            ).status_code, 401)
