import sys
import random
import datetime
import time
from dateutil import parser
from algo_trader.clients import BitmexOrder
import requests
import os


class Lotus:
    def __init__(self, client, symbols, settings, setting_file_name):
        self.client = client
        self.symbols = symbols
        self.settings = settings
        if self.client.testnet:
            from algo_trader.settings import TESTNET_LOTUS_LINK
            self._api_endpoint = TESTNET_LOTUS_LINK
        else:
            from algo_trader.settings import LIVE_LOTUS_LINK
            self._api_endpoint = LIVE_LOTUS_LINK
        self._settings_path = os.path.abspath(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), os.pardir, 'settings', setting_file_name))

        self._last_timestamp = {}
        self._last_entry = {}
        self._last_sl = {}

        for symbol in symbols:
            self._last_timestamp[symbol] = datetime.datetime.utcnow()
            self._last_entry[symbol] = ''
            self._last_sl[symbol] = ''

        if not self.client.is_connected:
            print(
                "Invalid API ID or API Secret, please restart and provide the right keys", flush=True)
            sys.exit()

    def is_new_signal(self, signal, symbol):
        timestamp = parser.parse(signal[symbol]['timestamp'])
        if self._last_timestamp[symbol] != timestamp:
            self._last_timestamp[symbol] = timestamp
            if self._last_entry[symbol] != signal[symbol]['entry'] or self._last_sl[symbol] != signal[symbol]['stoploss']:
                self._last_entry[symbol] = signal[symbol]['entry']
                self._last_sl[symbol] = signal[symbol]['stoploss']
                return True

    def get_api_signal(self):
        auth = {'token': self.settings.token}
        try:
            return requests.get(self._api_endpoint, params=auth).json()
        except ValueError:
            print("Can't get signal on endpoint {} with token {}. Please make sure your token is the right one and endpoint is set correct."
                  "It could also be that you are timed out because you try to access with multiple IP's. In this case wait 40 minutes and try again.".format(
                      self._api_endpoint, self.settings.token))
            return False

    def rand_sec(self, start=1, end=10):
        return random.randrange(start, end)

    def check_modify(self, symbol, sl):
        res = self.order.modifiy_stop(symbol, sl)
        if type(res) is str:
            print('Modify order Error:', res, flush=True)
        else:
            print('Modifying order in {} to new stoploss: {}'.format(
                symbol, sl), flush=True)
            self.order.SL = sl

    def process_signals(self, start=False):
        ns = self.get_api_signal()  # new signals
        if ns:
            for symbol in self.symbols:
                entry = ns[symbol]['entry']
                stoploss = ns[symbol]['stoploss']
                if start:
                    self.order.check_open_bot_order(symbol, entry, stoploss)
                    time.sleep(3)
                if self.is_new_signal(ns, symbol):
                    signal = ns[symbol]['signal']
                    if signal in [-1, 1]:  # signal has open position
                        if signal == 1:
                            if self.order.props[symbol]['qty'] > 0 or self.client.open_contracts(symbol) > 0:
                                self.check_modify(symbol, stoploss)
                            elif self.client.open_contracts(symbol) < 0:
                                print('Closing {} order.'.format(
                                    symbol), flush=True)
                                close = self.order.close(
                                    symbol, qty=-self.order.props[symbol]['qty'])
                                if close:
                                    print('Closed open Bot old short position in {}, because now the Bot\'s Position is long.'.format(
                                        symbol), flush=True)
                                else:
                                    print('Error closing {} order.'.format(
                                        symbol), flush=True)
                            else:
                                cp = self.client.last_current_price(symbol)
                                if cp < entry:
                                    sl_dist = abs(stoploss-cp)
                                    if sl_dist > 0.15 * sl_dist:
                                        time.sleep(2)
                                        contracts = self.order.calc_pos_size(
                                            symbol, sl_dist)
                                        print("Open market stop order long into open Signal. {} {} Contracts, Stoploss: {}".format(
                                            symbol, contracts, stoploss), flush=True)
                                        self.order.bracket_market_order(
                                            symbol, contracts, stoploss)
                        else:
                            if self.order.props[symbol]['qty'] < 0 or self.client.open_contracts(symbol) < 0:
                                self.check_modify(symbol, stoploss)
                            elif self.client.open_contracts(symbol) > 0:
                                print('Closing order on {}.'.format(
                                    symbol), flush=True)
                                close = self.order.close(qty=-self.order.props[symbol]['qty'])
                                if close:
                                    print('Closed open Bot old long position in {}, because now the Bot\'s Position is short.'.format(
                                        symbol), flush=True)
                                else:
                                    print('Error closing {} order.'.format(
                                        symbol), flush=True)
                            else:
                                cp = self.client.last_current_price(symbol)
                                if cp > entry:
                                    sl_dist = abs(entry-cp)
                                    if sl_dist > 0.15 * sl_dist:
                                        time.sleep(2)
                                        contracts = self.order.calc_pos_size(
                                            symbol, sl_dist)
                                        print("Open market stop order short into open Signal. {} {} Contracts, Stoploss: {}".format(
                                            symbol, contracts, stoploss), flush=True)
                                        self.order.bracket_market_order(
                                            symbol, -contracts, stoploss)
                    elif signal in [-2, 2]:  # signal has pending order
                        if self.order.props[symbol]['wait_stop']:
                            print("Cancel old order {} first.".format(symbol))
                            self.order.stoporder_cancel()  # cancel old order first
                            time.sleep(3)
                        contracts = self.order.calc_pos_size(
                            symbol, abs(entry - stoploss))
                        if self.order.props[symbol]['open']:
                            print("New signal is bracket stop long, but one bot order is open... closing open order in {}.".format(
                                symbol), flush=True)
                            self.order.close(symbol)
                            time.sleep(3)
                        if signal == 2:
                            if self.order.props[symbol]['qty'] < 0:
                                print(
                                    "Canceling stop order in other direction.", flush=True)
                                self.order.stoporder_cancel(symbol)
                                time.sleep(3)
                            print("Open bracket stop order long. {} {} Contracts, Entry: {}, Stoploss: {}".format(
                                symbol, contracts, entry, stoploss), flush=True)
                            self.order.bracket_stop_order(
                                symbol, contracts, entry, stoploss)
                        else:
                            if self.order.props[symbol]['qty'] > 0:
                                print(
                                    "Canceling stop order in other direction.", flush=True)
                                self.order.stoporder_cancel(symbol)
                                time.sleep(3)
                            print("Open bracket stop order short. {} {} Contracts, Entry: {}, Stoploss: {}".format(
                                symbol, contracts, entry, stoploss), flush=True)
                            self.order.bracket_stop_order(
                                symbol, -contracts, entry, stoploss)
                    else:
                        if self.order.props[symbol]['open']:
                            self.order.close(symbol)

    def run(self):
        # Main loop
        self.order = BitmexOrder(self.symbols,
                                 self.client, self.settings, self._settings_path)
        self.process_signals(start=True)
        while True:
            time.sleep(10)
            self.order.manage_entries(self.symbols)
            if datetime.datetime.now().minute % 30 == 0:
                time.sleep(19 + self.rand_sec(start=3))
                self.process_signals(self.symbols)
                time.sleep(40)
