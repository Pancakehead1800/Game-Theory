
import numpy as np


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