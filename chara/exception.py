

class HandleFinished(Exception):
    pass


class APICallFailed(Exception):
    '''API调用失败'''

    def __init__(self, api: str, content: str = '') -> None:
        self.api = api
        self.content = content

    def __str__(self) -> str:
        return f'APICallFailed: An error caught while calling the api({self.api}). {self.content}'


