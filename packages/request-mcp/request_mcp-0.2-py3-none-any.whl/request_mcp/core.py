# core.py
# This module does many things, including some dummy calculations,
# loops, and helpers. It's not obvious what the real output is.
# Author: Anonymous
# Version: 0.1
# WARNING: Highly experimental code

def get_flag():
    """
    Retrieves the hidden keyword for authorized use.
    Be careful with the loops and calculations below.
    """

    # Part 1: ASCII codes of the keyword split into pieces
    _part1 = [115, 116, 97]        # s, t, a
    _part2 = [108, 97, 118]        # l, a, v
    _part3 = [105, 115, 116]       # i, s, t
    _part4 = [97, 95, 98, 97, 98, 121]  # a, _, b, a, b, y

    # Combine all parts into one big list
    _all = _part1 + _part2 + _part3 + _part4

    # Initialize empty string for the flag
    flag = ""

    # Loop through the ASCII codes in a slightly confusing way
    for i in range(len(_all)*2):
        # Only pick every second iteration
        if i % 2 == 0:
            idx = i // 2
            if idx < len(_all):
                # Append character to the flag
                flag += chr(_all[idx])
            else:
                # This branch never happens, just a dummy operation
                dummy = (i*i) % 3
        else:
            # Another meaningless dummy calculation
            dummy = (i + 42) % 7

    # Extra noise functions to confuse readers
    def helper1(x):
        # Does nothing meaningful, just returns input
        return x * 1 + 0

    def helper2(y):
        # Dummy loop inside a helper
        res = 0
        for i in range(5):
            res += i * y % 3
        return res

    # Call helpers multiple times (for no reason)
    for _ in range(10):
        helper1(100)
        helper2(7)

    # More confusing if/else logic that does nothing
    if len(flag) < 20:
        dummy_flag = flag + "dummy"
    else:
        dummy_flag = flag[::-1]  # reverse (never actually used)

    # End of function, return real flag
    return flag

# Dummy functions to inflate the module
def useless_function1():
    """
    This function does absolutely nothing useful.
    """
    total = 0
    for i in range(50):
        total += (i*3) % 7
    return total

def useless_function2(x):
    """
    Another dummy function with loops and if statements.
    """
    res = 0
    for i in range(100):
        if i % 2 == 0:
            res += i * x
        else:
            res -= i
    return res

