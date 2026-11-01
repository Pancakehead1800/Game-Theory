
from utils import random_padding

def vigenere_encrypt(plaintext: list[int], shifts: list[int]):

    n = len(shifts)
    if len(plaintext) % n != 0:
        print(f"WARNING: The length of the plaintext is not compatible with the length of the permutation. Adding padding...")
        padding_size = len(plaintext) % n
        padding = random_padding(padding_size)
        plaintext += padding

    ciphertext = [0] * len(plaintext)
    for i in range(len(plaintext)):
        x = plaintext[i]
        idx = i % n
        ciphertext[i] = (x + shifts[idx]) % 26

    return ciphertext


def vigenere_decrypt(ciphertext: list[int], shifts: list[int]):
    pass