from api.bitmexWS import BitmexWebsocket


class BitmexAPI:
    def __init__(self, BASE_URL, SYMBOL, API_KEY, SECRET_KEY, SUBSCRIPTIONS) -> None:
        self.__name__ = 'bitmexAPI'
        self.ws = BitmexWebsocket(
            BASE_URL, SYMBOL, API_KEY, SECRET_KEY, SUBSCRIPTIONS)
