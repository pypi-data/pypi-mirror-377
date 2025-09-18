# core.py
# Obfuscated core for CTF: reconstructs the hidden string
# Author: Anonymous
# Version: 0.1
# NOTE: keep this file intentionally noisy for the challenge

def get_flag():
    """
    Reconstruct and return the hidden keyword.
    The ascii pieces are intentionally split and shuffled
    to make casual inspection harder.
    """

    # Part 1: correct ordering so the final string starts with 'a'
    # a, s, t
    _part1 = [97, 115, 116]        # 97='a', 115='s', 116='t'
    _part2 = [108, 97, 118]        # l, a, v
    _part3 = [105, 115, 116]       # i, s, t
    _part4 = [97, 95, 98, 97, 98, 121]  # a, _, b, a, b, y

    # Combine all parts into one big list
    _all = _part1 + _part2 + _part3 + _part4

    # Initialize empty string for the flag
    flag = ""

    # Loop through the ASCII codes in a slightly confusing way
    # This loop intentionally runs twice the length and only picks
    # even iterations to add noise.
    for i in range(len(_all) * 2):
        if i % 2 == 0:
            idx = i // 2
            if idx < len(_all):
                # Append character to the flag
                flag += chr(_all[idx])
            else:
                # Unreachable branch used as obfuscation
                _ = (i * i) % 3
        else:
            # Another meaningless dummy calculation to add noise
            _ = (i + 42) % 7

    # Extra noise functions to confuse readers (no effect on flag)
    def helper1(x):
        # Returns x unchanged (keeps static analysis noisy)
        return x * 1 + 0

    def helper2(y):
        # Dummy loop inside a helper
        res = 0
        for j in range(5):
            res += (j * y) % 3
        return res

    # Call helpers multiple times (for no reason)
    for _ in range(10):
        helper1(100)
        helper2(7)

    # Return the reconstructed flag
    return flag


# Several useless functions to bloat the module file
def useless_function1():
    """
    This function does absolutely nothing useful, but inflates file size.
    """
    total = 0
    for i in range(50):
        total += (i * 3) % 7
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

