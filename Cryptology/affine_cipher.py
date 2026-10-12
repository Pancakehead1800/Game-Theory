import math


def character_frequencies(text):
    freqs = {}
    for char in text:
        freqs[char] = freqs.get(char, 0) + 1
    return tuple(sorted(freqs.items(), key=lambda item: -item[1]))


def affine_decrypt(ciphertext, a, b):
    if math.gcd(a, 26) != 1:
        raise ValueError(f"There is no modular inverse to {a} mod 26, but {a} and 26 must be coprime!")
    a_inv = pow(a, -1, 26)
    ciphertext = ciphertext.upper()

    plaintext = ""
    for char in ciphertext:
        if char.isalpha():
            # Encode A...Z -> 1...26
            y = ord(char) - ord('A') + 1
            x = (a_inv * (y - b)) % 26
            plaintext += chr(x + ord('A') - 1)
        else:
            plaintext += char
    plaintext = plaintext.lower()
    return plaintext

def affine_encrypt(plaintext, a, b):
    if math.gcd(a, 26) != 1:
        raise Warning(f"There is no modular inverse to {a} mod 26!")
    plaintext = plaintext.lower()

    ciphertext = ""
    for char in plaintext:
        if char.isalpha():
            x = ord(char) - ord('a') + 1
            y = (a * x + b) % 26
            ciphertext += chr(y + ord('a') - 1)
        else:
            plaintext += char
    ciphertext = ciphertext.upper()
    return ciphertext
