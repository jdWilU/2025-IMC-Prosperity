import itertools

# Define conversion rates as a dictionary of dictionaries.
# Each conversion is represented as: from_asset -> {to_asset: conversion_rate}
conversions = {
    "SeaShells": {"Snowballs": 1.34, "Silicon Nuggets": 0.64},
    "Snowballs": {"Silicon Nuggets": 0.52, "Pizza's": 1.45},
    "Silicon Nuggets": {"Pizza's": 3.1, "SeaShells": 1.49},
    "Pizza's": {"SeaShells": 0.48}
}

# Recursive search for cycles that start and end at the starting_asset.
def find_cycles(starting_asset, current_asset, current_cycle, current_multiplier, max_depth, cycles):
    # If depth > 0 and we've returned to our starting asset, and we have at least one conversion
    if current_asset == starting_asset and current_cycle:
        if current_multiplier > 1:
            cycles.append((list(current_cycle), current_multiplier))
        # Note: Do not continue expanding this path to avoid infinite loops once a valid cycle is reached.
        # If you want cycles with repeated asset trades, you could choose to continue.
        return

    if len(current_cycle) >= max_depth:
        return
    
    # For each possible conversion from the current asset:
    for next_asset, rate in conversions.get(current_asset, {}).items():
        # Avoid immediate reversal if you wish, or impose other rules to reduce repeated cycles.
        current_cycle.append((current_asset, next_asset))
        new_multiplier = current_multiplier * rate
        find_cycles(starting_asset, next_asset, current_cycle, new_multiplier, max_depth, cycles)
        current_cycle.pop()

def run_simulation(starting_asset="SeaShells", max_depth=5):
    cycles = []
    find_cycles(starting_asset, starting_asset, [], 1, max_depth, cycles)
    return cycles

if __name__ == "__main__":
    found_cycles = run_simulation(max_depth=500)  # Adjust max_depth as needed
    # Sort cycles by net multiplier (highest first)
    best_cycles = sorted(found_cycles, key=lambda x: x[1], reverse=True)
    
    print("Found profitable cycles:")
    for cycle, multiplier in best_cycles:
        # Format cycle as a path string
        path_str = " → ".join([trade[0] for trade in cycle] + [cycle[-1][1]] if cycle else [starting_asset])
        print(f"Cycle: {path_str}, Net Multiplier: {multiplier:.4f}")
