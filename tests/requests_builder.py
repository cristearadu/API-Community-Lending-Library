import requests


def http_request(method, url, headers, json=None, files=None):
    return requests.request(
        method=method, url=url, headers=headers, json=json, files=files
    )


def get(self, url, headers, json):
    return self.request(method="GET", url=url, headers=headers, json=json)


def post(self, url, headers, json):
    return self.request(method="POST", url=url, headers=headers, json=json)


def delete(self, url, headers, json):
    return self.request(method="DELETE", url=url, headers=headers, json=json)


def patch(self, url, headers, json):
    return self.request(method="PATCH", url=url, headers=headers, json=json)
