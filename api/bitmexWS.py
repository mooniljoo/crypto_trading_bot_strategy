from time import sleep
from config.subscriptions import NO_SYMBOL_SUBS, NO_AUTH_SUBS, DEFAULT_SUBS
import time
import sys
import websocket
import requests
import threading
import hmac
import hashlib
import json
import math
import urllib
import telegram
import dateutil.parser
import pytz
import traceback


def toLocalTime(utctime):
    date = dateutil.parser.parse(utctime)
    local_timezone = pytz.timezone('Asia/Seoul')
    local_date = date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_date.strftime("%Y년%m월%d일 %H시%M분%S초 %f")


def generate_nonce():
    return int(round(time.time() + 3600))


def generate_signature(secret, verb, url, nonce, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsedURL = urllib.parse.urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query

    # print "Computing HMAC: %s" % verb + path + str(nonce) + data
    message = (verb + path + str(nonce) + data).encode('utf-8')

    signature = hmac.new(secret.encode('utf-8'), message,
                         digestmod=hashlib.sha256).hexdigest()
    return signature


class BitmexWebsocket:

    def __init__(self, base_url=None, symbol=None, api_key=None, secret_key=None, subscriptions=['trade']):
        # self.data = {"quote": [{"bidPrice": 20000}]}
        '''Connect to the websocket and initialize data stores.'''
        print("Initializing WebSocket.")
        # Don't grow a table larger than this amount. Helps cap memory usage.
        self.MAX_TABLE_LEN = 200

        self.api_key = api_key
        self.secret_key = secret_key

        self.base_url = base_url
        self.symbol = symbol

        self.activeOrders = []
        self.filledOrders = []

        self.data = {}
        self.keys = {}
        self.exited = False
        self.beingClosed = False
        self._error = None

        # Prepare HTTPS session
        self.session = requests.Session()
        # These headers are always sent
        self.session.headers.update({'content-type': 'application/json'})
        self.session.headers.update({'accept': 'application/json'})

        # We can subscribe right in the connection querystring, so let's build that.
        # Subscribe to all pertinent base_urls
        self.wsURL = self.__get_url(subscriptions)
        print("Connecting to %s" % self.wsURL)
        self.__connect(self.wsURL, symbol)
        print('Connected to WS.')

        #
        # wait for partials
        #
        # wait for {'instrument', 'trade', 'quote'}
        # self.__wait_for_symbol(symbol)
        # if api_key:
        # waite for {'margin', 'position', 'order'}
        # self.__wait_for_account()
        print(
            'Got all initial market data. (just finished setting the tables for data)')

    def __del__(self):
        self.exit()

    #
    # Lifecycle methods
    #
    def error(self, err):
        self._error = err
        if "WinError" in err:
            self.reset()
        else:
            self.exit()
        print(err)

    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.exited = True
        self.ws.close()

    def get_instrument(self):
        '''Get the raw instrument data for this symbol.'''
        # Turn the 'tickSize' into 'tickLog' for use in rounding
        instrument = self.data['instrument'][0]
        # tickSize is the minimum price movement of a trading instrument.
        # ex) 틱 사이즈가 10이면 틱로그는 1, 100이면 틱로그는 2
        instrument['tickLog'] = int(
            math.fabs(math.log10(instrument['tickSize'])))
        return instrument

    def get_ticker(self):
        '''Return a ticker object. Generated from quote and trade.'''
        lastQuote = self.data['quote'][-1]
        lastTrade = self.data['trade'][-1]
        ticker = {
            "최근체결가": lastTrade['price'],
            "bid": lastQuote['bidPrice'],
            "ask": lastQuote['askPrice'],
            "mid": (float(lastQuote['bidPrice'] or 0) + float(lastQuote['askPrice'] or 0)) / 2
        }

        # The instrument has a tickSize. Use it to round values.
        # tickLog is to round up the price to the digits when marking the price.
        # instrument = self.data['instrument'][0]
        return ticker

    #
    # Data Methods
    #
    def funds(self):
        '''Get your margin details.'''
        return self.data['margin'][0]

    def positions(self):
        '''Get your positions.'''
        return self.data['position']

    def orders(self, clOrdIDPrefix=None):
        '''Get your orders'''
        orders = self.data['order']
        if clOrdIDPrefix:
            return [o for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix)]
        else:
            return orders

    def market_depth(self):
        '''Get market depth (orderbook). Returns all levels.'''
        return self.data['orderBookL2']

    def recent_trades(self):
        '''Get recent trades.'''
        return self.data['trade']

    def get_active_orders(self, clOrdIDPrefix=None):
        orders = self.data['order']
        # Filter to only open orders (leavesQty > 0) and those that we actually placed

        if clOrdIDPrefix:
            return [o for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and o['leavesQty'] > 0]
        else:
            return [o for o in orders if o['leavesQty'] > 0]

    def __connect(self, wsURL, symbol):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth())

        print("Try to start thread")
        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()
        print("Thread started")

        # Wait for connect before continuing
        conn_timeout = 5
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout and not self._error:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout or self._error:
            print("Couldn't connect to WS! Exiting.")
            self.exit()
            sys.exit(1)

    def __get_auth(self):
        '''Return auth headers. Will use API Keys if present in settings.'''

        if self.shouldAuth is False:
            return {}
        if self.api_key:
            print("Authenticating with API Key.")
            # To auth to the WS using an API key, we generate a signature of a nonce and
            # the WS API base_url.
            expires = generate_nonce()
            return {
                "api-expires": str(expires),
                "api-signature":
                generate_signature(self.secret_key, 'GET',
                                   '/realtime', expires, ''),
                "api-key": self.api_key
            }
        else:
            print("Not authenticating.")
            return {}

    def __get_url(self, subscriptions, shouldAuth=True):
        '''
        Generate a connection URL. We can define subscriptions right in the querystring.
        Most subscription topics are scoped by the symbol we're listening to.
        '''
        self.shouldAuth = shouldAuth
        if self.shouldAuth:
            # Some subscriptions need to have the symbol appended.
            subscriptions_full = map(lambda sub: (
                sub if sub in NO_SYMBOL_SUBS
                else (sub + ':' + self.symbol)
            ), subscriptions)
        else:
            subscriptions_full = NO_AUTH_SUBS
        print(subscriptions)

        urlParts = list(urllib.parse.urlparse(self.base_url))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(
            ','.join(subscriptions_full))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        # Wait for the keys to show up from the ws
        # 값이 self.data에 없으면 while 문을 통해 0.1초 sleep하며 반복
        # while not {'margin', 'position', 'order', 'orderBookL2'} <= set(self.data):
        while not {'margin', 'position', 'order'} <= set(self.data):
            sleep(0.1)

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        # while not {'instrument', 'trade', 'quote'} <= set(self.data):
        while not {'trade', 'quote'} <= set(self.data):
            sleep(0.1)

    def __on_message(self, ws, message):
        '''Handler for parsing WS messages.'''
        message = json.loads(message)
        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        try:
            if 'subscribe' in message:
                if message['success']:
                    print("Subscribed to %s." %
                          message['subscribe'])
                else:
                    self.error("Unable to subscribe to %s. Error: \"%s\" Please check and restart." %
                               (message['request']['args'][0], message['error']))
            elif 'status' in message:
                if message['status'] == 400:
                    self.error(message['error'])
                if message['status'] == 401:
                    self.error("API Key incorrect, please check and restart.")
            elif action:

                if table not in self.data:
                    self.data[table] = []

                if table not in self.keys:
                    self.keys[table] = []

                # There are four possible actions from the WS:
                # 'partial' - full table image
                # 'insert'  - new row
                # 'update'  - update row
                # 'delete'  - delete row
                if action == 'partial':
                    # print("%s: partial" % table)
                    self.data[table] += message['data']
                    # Keys are communicated on partials to let you know how to uniquely identify
                    # an item. We use it for updates.
                    self.keys[table] = message['keys']
                elif action == 'insert':
                    # print('%s: inserting %s' %
                    #       (table, message['data']))
                    self.data[table] += message['data']

                    # Limit the max length of the table to avoid excessive memory usage.
                    # Don't trim orders because we'll lose valuable state if we do.
                    if table != 'order' and len(self.data[table]) > self.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][(
                            self.MAX_TABLE_LEN // 2):]

                elif action == 'update':
                    # print('%s: updating %s' %
                    #       (table, message['data']))
                    # Locate the item in the collection and update it.
                    for updateData in message['data']:
                        item = findItemByKeys(
                            self.keys[table], self.data[table], updateData)
                        if not item:
                            return  # No item found to update. Could happen before push

                        # Log executions
                        is_canceled = 'ordStatus' in updateData and updateData['ordStatus'] == 'Canceled'
                        if table == 'order' and 'leavesQty' in updateData and not is_canceled:
                            instrument = self.get_instrument(item['symbol'])
                            contExecuted = abs(
                                item['leavesQty'] - updateData['leavesQty'])
                            print("Execution: %s %d Contracts of %s at %.*f" %
                                  (item['side'], contExecuted, item['symbol'],
                                   instrument['tickLog'], item['price']))

                        item.update(updateData)
                        # Remove cancelled / filled orders
                        if table == 'order' and item['leavesQty'] <= 0:
                            self.data[table].remove(item)
                elif action == 'delete':
                    # print('%s: deleting %s' %
                    #       (table, message['data']))
                    # Locate the item in the collection and remove it.
                    for deleteData in message['data']:
                        item = findItemByKeys(
                            self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("Unknown action: %s" % action)
        except:
            print(traceback.format_exc())

    def __on_open(self, ws):
        print("Websocket Opened.")

    def __on_close(self, ws):
        print('### Websocket Closed ###')
        self.exit()

    def __on_error(self, ws, error):
        if not self.exited:
            self.error(error)

    def reset(self):
        self.__reset()
        self.__connect(self.wsURL, self.symbol)

    def __reset(self):
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None


# Utility method for finding an item in the store.
# When an update comes through on the websocket, we need to figure out which item in the array it is
# in order to match that item.
#
# Helpfully, on a data push (or on an HTTP hit to /api/v1/schema), we have a "keys" array. These are the
# fields we can use to uniquely identify an item. Sometimes there is more than one, so we iterate through all
# provided keys.
def findItemByKeys(keys, table, matchData):
    for item in table:
        if all(item[k] == matchData[k] for k in keys):
            return item


def order_leaves_quantity(o):
    if o['leavesQty'] is None:
        return True
    return o['leavesQty'] > 0


if __name__ == "__main__":
    from config import config
    ws = BitmexWebsocket(config.BASE_URL, config.SYMBOL,
                         config.API_KEY, config.SECRET_KEY)
    while 1:
        print("...running...")
        print(ws.data)
        sleep(1)
