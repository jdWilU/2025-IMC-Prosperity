from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math
import jsonpickle # Add import for jsonpickle if needed for traderData serialization later

class Trader:

    POSITION_LIMIT = {'AMETHYSTS': 20, 'STARFRUIT': 20}
    SPREAD = {'AMETHYSTS': 2, 'STARFRUIT': 4} # Wider spread for more volatile Starfruit

    def run(self, state: TradingState) -> (Dict[str, List[Order]], int, str):
        """
        Implements a market-making strategy based on calculating a fair value using WAP,
        applying spreads, and managing inventory within position limits.
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        result = {}
        conversions = 0 # No conversions needed for this basic strategy
        traderData = "" # No state data needed for this basic strategy yet

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position_limit = self.POSITION_LIMIT.get(product, 0)
            spread = self.SPREAD.get(product, 2) # Default spread if product not in dict

            # Calculate fair value using Weighted Average Price (WAP)
            fair_value = None
            if order_depth.sell_orders and order_depth.buy_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask] # Negative volume
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid] # Positive volume

                # Ensure volumes are non-zero before calculating WAP
                if abs(best_ask_volume) > 0 and best_bid_volume > 0:
                    wap = (best_bid * abs(best_ask_volume) + best_ask * best_bid_volume) / (best_bid_volume + abs(best_ask_volume))
                    fair_value = wap
                elif best_bid_volume > 0: # Only bids have volume
                    fair_value = best_bid # Use best bid as fair value
                elif abs(best_ask_volume) > 0: # Only asks have volume
                    fair_value = best_ask # Use best ask as fair value
                else: # Neither best bid nor best ask has volume, use midpoint?
                     fair_value = (best_bid + best_ask) / 2.0
            elif order_depth.buy_orders: # Only bids exist
                 best_bid = max(order_depth.buy_orders.keys())
                 fair_value = best_bid # Use best bid if no asks
            elif order_depth.sell_orders: # Only asks exist
                 best_ask = min(order_depth.sell_orders.keys())
                 fair_value = best_ask # Use best ask if no bids

            # Proceed only if a fair value could be determined
            if fair_value is not None and position_limit > 0:
                # Calculate buy and sell prices around the fair value
                buy_price = math.floor(fair_value - spread / 2)
                sell_price = math.ceil(fair_value + spread / 2)

                # Get current position and calculate allowable order volumes
                current_position = state.position.get(product, 0)
                buy_volume_allowed = position_limit - current_position  # Max volume we can buy
                sell_volume_allowed = position_limit + current_position # Max volume we can sell (position is negative when short)

                # Place buy order if allowed volume is positive
                if buy_volume_allowed > 0:
                    print(f"PLACING BUY Order for {product}: Price={buy_price}, Volume={buy_volume_allowed}")
                    orders.append(Order(product, buy_price, buy_volume_allowed))

                # Place sell order if allowed volume is positive
                if sell_volume_allowed > 0:
                    print(f"PLACING SELL Order for {product}: Price={sell_price}, Volume={-sell_volume_allowed}") # Sell volume must be negative
                    orders.append(Order(product, sell_price, -sell_volume_allowed))

            result[product] = orders

        # Update traderData if needed for state persistence (e.g., using jsonpickle)
        # traderData = jsonpickle.encode({}) # Example

        return result, conversions, traderData