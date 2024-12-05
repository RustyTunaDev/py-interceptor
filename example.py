import http.client
import json
from typing import Dict, Optional

from interceptor import intercept, InterceptInfo


class RestClient:

    def __init__(self, base_url: str):
        self._base_url = base_url
        self._connection: Optional[http.client.HTTPSConnection] = None
        self._headers = {'Content-type': 'application/json'}

    def connect(self):
        self._connection = http.client.HTTPSConnection(self._base_url)

    def request(self, req_type: str, url: str, data: str, headers: Dict[str, str]) -> Dict:
        self._connection.request(req_type, url, data, headers)
        response = self._connection.getresponse()
        return json.loads(response.read())

    def post(self, url: str, data: Dict) -> Dict:
        return self.request("POST", url, json.dumps(data), self._headers)

    def patch(self, url: str, data: Dict) -> Dict:
        return self.request("PATCH", url, json.dumps(data), self._headers)

    def get(self, url: str, data: Dict) -> Dict:
        return self.request("GET", url, json.dumps(data), self._headers)

    def delete(self, url: str, data: Dict) -> Dict:
        return self.request("DELETE", url, json.dumps(data), self._headers)


class Interceptor:

    def __init__(self):
        self._logs = []

    def __call__(self, info: InterceptInfo):
        self._logs.append(info)
        ret_maps = {
            "POST": {"status_code": "created"},
            "PATCH": {"status_code": "updated"},
            "GET": {"status_code": "ok", "a": 1, "b": 2, "c": 3},
            "DELETE": {"status_code": "deleted"},
        }
        if info.name == "request":
            return ret_maps[info.args[0]]

    def print_logs(self):
        self._logs.sort(key=lambda log: log.timestamp)
        for log in self._logs:
            print(log)


if __name__ == "__main__":
    client = RestClient("localhost:8080")
    interceptor = Interceptor()
    intercept({"post", "patch", "get", "delete"}, client, interceptor, blocking=False)
    intercept({"connect", "request"}, client, interceptor, blocking=True)

    client.connect()
    client.post("/new", {"a": 1, "b": 2, "c": 3})
    client.patch("/update", {"a": 4, "b": 5, "c": 6})
    client.get("/get", {"a": 7})
    client.delete("/delete", {"a": 8})
    interceptor.print_logs()
