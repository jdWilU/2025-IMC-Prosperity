from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math

class Trader:

    # Updated position limits and spreads for Round 1 products
    POSITION_LIMIT = {
        'RAINFOREST_RESIN': 50,
        'KELP': 50,
        'SQUID_INK': 50
    }
    SPREAD = {
        'RAINFOREST_RESIN': 2,  # Tight spread for stable product
        'KELP': 5,              # Wider spread for volatile product
        'SQUID_INK': 4          # Moderate spread for swings with potential pattern
    }

    def run(self, state: TradingState) -> (Dict[str, List[Order]], int, str):
        """
        Market-making strategy with WAP-based fair value, product-specific spreads,
        and position limit management for Round 1 products.
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        result = {}
        conversions = 0
        traderData = ""

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position_limit = self.POSITION_LIMIT.get(product, 0)
            spread = self.SPREAD.get(product, 2)  # Default to 2 if product not recognized

            # Calculate fair value using WAP
            fair_value = None
            if order_depth.sell_orders and order_depth.buy_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]  # Negative
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]   # Positive

                if abs(best_ask_volume) > 0 and best_bid_volume > 0:
                    wap = (best_bid * abs(best_ask_volume) + best_ask * best_bid_volume) / (best_bid_volume + abs(best_ask_volume))
                    fair_value = wap
                elif best_bid_volume > 0:
                    fair_value = best_bid
                elif abs(best_ask_volume) > 0:
                    fair_value = best_ask
                else:
                    fair_value = (best_bid + best_ask) / 2.0
            elif order_depth.buy_orders:
                fair_value = max(order_depth.buy_orders.keys())
            elif order_depth.sell_orders:
                fair_value = min(order_depth.sell_orders.keys())

            if fair_value is not None and position_limit > 0:
                # Calculate buy and sell prices
                buy_price = math.floor(fair_value - spread / 2)
                sell_price = math.ceil(fair_value + spread / 2)

                # Position management
                current_position = state.position.get(product, 0)
                buy_volume_allowed = position_limit - current_position
                sell_volume_allowed = position_limit + current_position

                # Place orders with volume control
                if buy_volume_allowed > 0:
                    buy_volume = min(buy_volume_allowed, 10)  # Cap at 10 for safety
                    print(f"PLACING BUY Order for {product}: Price={buy_price}, Volume={buy_volume}")
                    orders.append(Order(product, buy_price, buy_volume))

                if sell_volume_allowed > 0:
                    sell_volume = min(sell_volume_allowed, 10)  # Cap at 10 for safety
                    print(f"PLACING SELL Order for {product}: Price={sell_price}, Volume={-sell_volume}")
                    orders.append(Order(product, sell_price, -sell_volume))

            result[product] = orders

        return result, conversions, traderData