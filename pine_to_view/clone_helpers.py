

from coin_class import ApiTradingClient
from coinswitch import get_instrument_info

class CloneHelpers:

    def execution_flow_for_cloning(self, api_key, secret_key, symbol):
        min_qty_symbol, max_leverage_coinswitch = get_instrument_info(api_key, secret_key, symbol)
        


