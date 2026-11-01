
import numpy as np
import math
from collections import Counter



# ============ HELPFUL FUNCTIONS ============ #


# Turn string of letters to numbers (ignoring non-alphabetic characters)
def encode_text(text: str) -> list:
    # turn all letters into numbers, regardless of case
    # a, b, c, ... -> 0, 1, 2, ...
    # NOTE: special characters will be passed as strings into the resulting list
    text = text.lower()
    res = [-1] * len(text)

    for i in range(len(text)):
        char = text[i]
        if not char.isalpha():
            res[i] = char
        else:
            res[i] = ord(char) - ord('a')

    return res

# Turn list of numbers back into a string
def decode_text(text: list) -> str:
    # turn list of numbers into letters
    res = ""

    for char in text:
        if isinstance(char, str):
            res += char
        else:
            res += chr(char + ord('a'))

    return res

        

# Count frequencies of characters
def character_frequencies(text):
    freqs = {}
    for char in text:
        freqs[char] = freqs.get(char, 0) + 1
    return tuple(sorted(freqs.items(), key=lambda item: -item[1]))



# Check if a list of length n is truly a permutation of [n] = {1, 2, ..., n-1, n}
def check_permutation(nums):
    n = len(nums)
    seen = [False] * (n+1)

    for num in nums:
        if num <= 0 or n < num:
            return False
        if seen[num]:
            return False
        seen[num] = True

    return True



# Generate a list of random numbers to add as padding
def random_padding(length):
    rng = np.random.default_rng()
    nums = rng.integers(0, 27, size=length)
    return list(nums)


# compute index of coincidence
def index_of_coincidence(x: list[int], y: list[int]):
    if len(x) != len(y):
        print(f"WARNING: x={x} and y={y} not the same length")

    n = min(len(x), len(y))
    N = max(len(x), len(y))
    coincidences = 0
    for i in range(n):
        if x[i] == y[i]:
            coincidences += 1

    index = (1.0 / N) * coincidences
    return index

# compute index of coincidence for single sequence
def single_index_of_coincidence(seq):
    n = len(seq)
    if n < 2:
        return 0.0

    frequencies = Counter(seq)
    numerator = sum(f * (f-1) for f in frequencies.values())
    return numerator / (n * (n-1))
