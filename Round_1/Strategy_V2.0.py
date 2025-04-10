from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math
import numpy as np

class Trader:
    # Position limits and initial spreads
    POSITION_LIMIT = {
        'RAINFOREST_RESIN': 50,
        'KELP': 50,
        'SQUID_INK': 50
    }
    
    # Historical price windows for different products
    PRICE_HISTORY = {
        'RAINFOREST_RESIN': [],
        'KELP': [],
        'SQUID_INK': []
    }
    
    # Maximum history length
    MAX_HISTORY = 100
    
    # Volatility thresholds for adjusting spreads
    VOLATILITY_THRESHOLDS = {
        'RAINFOREST_RESIN': 0.001,  # 0.1%
        'KELP': 0.002,             # 0.2%
        'SQUID_INK': 0.002         # 0.2%
    }
    
    # Base spreads
    BASE_SPREAD = {
        'RAINFOREST_RESIN': 2,
        'KELP': 5,
        'SQUID_INK': 4
    }
    
    def update_price_history(self, product: str, price: float):
        """Update price history maintaining fixed window size"""
        self.PRICE_HISTORY[product].append(price)
        if len(self.PRICE_HISTORY[product]) > self.MAX_HISTORY:
            self.PRICE_HISTORY[product] = self.PRICE_HISTORY[product][-self.MAX_HISTORY:]
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility based on historical prices"""
        if len(prices) < 2:
            return 0
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns)
    
    def calculate_trend(self, prices: List[float]) -> float:
        """Calculate price trend using simple moving average"""
        if len(prices) < 10:
            return 0
        prices_array = np.array(prices)
        short_ma = np.mean(prices_array[-5:])
        long_ma = np.mean(prices_array[-10:])
        return (short_ma - long_ma) / long_ma
    
    def calculate_dynamic_spread(self, product: str, volatility: float, trend: float) -> float:
        """Calculate dynamic spread based on volatility and trend"""
        base_spread = self.BASE_SPREAD[product]
        volatility_factor = 1 + (volatility / self.VOLATILITY_THRESHOLDS[product])
        trend_factor = 1 + abs(trend)  # Increase spread when trend is strong
        return base_spread * volatility_factor * trend_factor
    
    def calculate_position_size(self, product: str, volatility: float, current_position: int) -> int:
        """Calculate position size based on volatility and current position"""
        position_limit = self.POSITION_LIMIT[product]
        max_position = position_limit - abs(current_position)
        
        # Reduce position size when volatility is high
        volatility_factor = 1 - min(volatility / self.VOLATILITY_THRESHOLDS[product], 0.5)
        return max(1, int(max_position * volatility_factor))
    
    def run(self, state: TradingState) -> (Dict[str, List[Order]], int, str):
        """
        Improved market-making strategy with:
        - Dynamic spreads based on volatility and trend
        - Position sizing based on volatility
        - Trend following capabilities
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        result = {}
        conversions = 0
        traderData = ""

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Get current position
            current_position = state.position.get(product, 0)
            
            # Calculate mid price and update price history
            if order_depth.sell_orders and order_depth.buy_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                self.update_price_history(product, mid_price)
            
            # Calculate market metrics
            volatility = self.calculate_volatility(self.PRICE_HISTORY[product])
            trend = self.calculate_trend(self.PRICE_HISTORY[product])
            
            # Calculate dynamic spread
            spread = self.calculate_dynamic_spread(product, volatility, trend)
            
            # Calculate position size
            position_size = self.calculate_position_size(product, volatility, current_position)
            
            # Place orders
            if order_depth.sell_orders and order_depth.buy_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                
                # Adjust prices based on trend
                buy_price = math.floor(best_bid + spread/2 - trend * spread)
                sell_price = math.ceil(best_ask - spread/2 - trend * spread)
                
                # Place buy order
                if current_position < self.POSITION_LIMIT[product]:
                    buy_volume = min(position_size, self.POSITION_LIMIT[product] - current_position)
                    if buy_volume > 0:
                        print(f"PLACING BUY Order for {product}: Price={buy_price}, Volume={buy_volume}")
                        orders.append(Order(product, buy_price, buy_volume))
                
                # Place sell order
                if current_position > -self.POSITION_LIMIT[product]:
                    sell_volume = min(position_size, self.POSITION_LIMIT[product] + current_position)
                    if sell_volume > 0:
                        print(f"PLACING SELL Order for {product}: Price={sell_price}, Volume={-sell_volume}")
                        orders.append(Order(product, sell_price, -sell_volume))
            
            result[product] = orders

        return result, conversions, traderData 