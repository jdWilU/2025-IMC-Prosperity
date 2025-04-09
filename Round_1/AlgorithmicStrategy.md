# Algorithmic Trading Strategy: Market-Making Summary

## Introduction
This strategy employs **market-making**, where you provide liquidity by placing buy and sell orders for each product. The aim is to profit from the bid-ask spread while controlling risk through inventory management. It’s a simple yet effective approach for a basic trading environment with a small number of products.

## Core Strategy Components

### 1. Estimate Fair Value
Determine a **fair value** for each product to guide your trading decisions.

- **Stable Products:**
  - Use a fixed fair value based on historical or sample data (e.g., 10,000 seashells if prices hover around that level).
- **Volatile Products:**
  - Calculate a dynamic fair value using:
    - **Midprice:** Average of the best bid and best ask from the order book.
    - **Moving Average:** Average of recent trade prices (e.g., last 5-10 trades).
    - **Volume-Weighted Average:** Weight order book prices by their quantities.

### 2. Place Orders Around Fair Value
Place buy and sell orders to capture the spread:

- **Buy Orders:** Set slightly below fair value (e.g., fair value - half the spread).
- **Sell Orders:** Set slightly above fair value (e.g., fair value + half the spread).
- **Spread Size:**
  - Small spread (e.g., 1-2 units) for stable products.
  - Wider spread (e.g., 4+ units) for volatile products.

**Example:**
- Fair value = 10,000, spread = 2:
  - Buy at 9,999
  - Sell at 10,001

### 3. Manage Inventory
Stay within position limits by balancing your inventory:

- **Track Position:** Monitor net position (long/short) after each trade.
- **Adjust Orders:**
  - **Long Position:** Lower sell prices or reduce buy orders to offload inventory.
  - **Short Position:** Raise buy prices or reduce sell orders to rebuild inventory.
- **Target:** Keep position near zero for flexibility and risk control.

### 4. Optional: Product Relationships
If multiple products exist, explore price correlations:

- Check if one product’s price affects another.
- Consider basic pairs trading if relationships are evident.
- Likely unnecessary for a simple round but worth noting.

## Implementation Tips
- **Data:** Use provided sample data to test fair value methods and price behavior.
- **Coding:** Implement in Python, processing order book/trade data and submitting orders each step.
- **Tuning:** Adjust spread size or averaging windows based on backtesting.

## Why It Works
- **Simplicity:** Easy to code and execute.
- **Profit:** Captures spread consistently.
- **Risk:** Inventory management prevents overexposure.

## Conclusion
This market-making strategy—estimating fair value, placing strategic orders, and managing inventory—offers a robust foundation for an introductory trading challenge. It’s adaptable to both stable and volatile products, ensuring profitability and risk control.