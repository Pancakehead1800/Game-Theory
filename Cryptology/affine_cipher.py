import math


# Input a list of numnbers, a, and b
def affine_encrypt(plaintext: list[int], a: int, b: int):

    if math.gcd(a, 26) != 1:
        print(f"Warning: there is no modular inverse to {a} mod 26. This is a bad idea!")

    ciphertext = []
    for x in plaintext:
        y = (a * x + b) % 26
        ciphertext.append(y)

    return ciphertext


def affine_decrypt(ciphertext: list[int], a: int, b: int):

    if math.gcd(a, 26) != 1:
        raise ValueError(f"There must be a modular inverse to {a} mod 26. Equivalently, {a} and 26 must be coprime. They are NOT!!!")

    a_inv = pow(a, -1, 26)

    plaintext = []
    for y in ciphertext:
        x = (a_inv * (y - b)) % 26
        plaintext.append(x)

    return plaintext


def affine_decrypt_brute(ciphertext: list[int]):
    pass

