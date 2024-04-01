import numpy as np

def priority(item: float, bins: np.ndarray):
    # Calculate the remaining space in each bin after adding the item        remaining_space = bins - item            # Prioritize bins that have a lot of available space and are already fairly empty        priorities = remaining_space * np.log(bins / remaining_space)            # We want to minimize the priority, so we return the negative of the priorities        return -priorities    
def get_valid_bin_indices(item: float, bins: np.ndarray) -> np.ndarray:
    """Returns indices of bins in which item can fit."""
    return np.nonzero((bins - item) >= 0)[0]