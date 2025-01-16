import json
from pathlib import Path
from typing import List

from interceptor import intercept, get_methods, CallInfo


class API:

    def add(self, a, b):
        return a + b

    def sub(self, a, b):
        return a - b

    def mul(self, a, b):
        return a * b

    def div(self, a, b):
        return a / b


class Processor:

    def __init__(self, api):
        self._api = api

    def calc_mean(self, a, b):
        return self._api.div(a=self._api.add(a, b), b=2)

    def calc_variance(self, a, b):
        mean = self.calc_mean(a, b)
        x = self._api.sub(a, mean)
        y = self._api.sub(b, mean)
        return self._api.div(self._api.mul(x, x) + self._api.mul(y, y), 2)


class JSONLogger:

    def __init__(self):
        self._logs: List[CallInfo] = []

    def __call__(self, info: CallInfo):
        self._logs.append(info)

    def save_as_json(self, path: Path):
        data = {"logs": []}
        for log in self._logs:
            data["logs"].append({
                "name": log.name,
                "args": log.args,
                "kwargs": log.kwargs,
                "ret_value": log.ret_value,
                "target": log.target.__name__,
                "timestamp_ns": log.timestamp_ns
            })
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    # Create Interceptor instance
    logger = JSONLogger()

    # Create API instance and mount it for interception
    api = API()
    intercept(get_methods(api), target=api, interceptor=logger, blocking=False)

    # Create Processor instance and mount it for interception
    processor = Processor(api)
    intercept(get_methods(processor), target=processor, interceptor=logger, blocking=False)

    # Execute processor methods and save logs
    print(processor.calc_variance(4, 2))
    logger.save_as_json(Path("logs.json"))
