
from utils import check_permutation

def substitution_encrypt(plaintext: list[int], permutation: list[int]):

    # permutation maps value i to value permutation[i]
    valid_permutation = check_permutation(permutation)
    if not valid_permutation:
        raise ValueError(f"The subsitution permutation given is not one-to-one and thus not decryptable!")

    ciphertext = [0] * len(plaintext)
    for i in range(len(plaintext)):
        x = plaintext[i]
        ciphertext[i] = permutation[x]

    return ciphertext


def substitution_decrypt(ciphertext: list[int], permutation: list[int]):
    pass

def substitution_decrypt_brute(ciphertext):
    pass
