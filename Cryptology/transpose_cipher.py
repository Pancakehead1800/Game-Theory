
from Cryptology.utils.cryptology import check_permutation, random_padding


def transpose_encrypt(plaintext: list[int], permutation: list[int]):
    print("The plaintext will be 1-indexed: 123...n 123...n 123...n.")


    valid_permutation = check_permutation(permutation)
    if not valid_permutation:
        raise ValueError(f"The permutation given is not a valid permutation: {permutation}")

    n = len(permutation)
    if len(plaintext) % n != 0:
        print(f"WARNING: The length of the plaintext is not compatible with the length of the permutation. Adding padding...")
        padding_size = len(plaintext) % n
        padding = random_padding(padding_size)
        plaintext += padding

    def apply_permutation(nums, permutation):
        return [nums[i] for i in permutation]

    blocks = len(plaintext) // n
    ciphertext = []
    for block in range(blocks):
        permuted_block = apply_permutation(plaintext[block * n: (block+1)*n])
        ciphertext += permuted_block

    return ciphertext


def transpose_decrypt(ciphertext: list[int], permutation: list[int]):

    # Just need to find the inverse permutation
    # permutation_inv(permutation(nums)) = nums

    n = len(permutation)
    inverse = [0] + [0] * n
    for idx, num in enumerate([0] + permutation):
        inverse[num] = idx
    inverse = inverse[1:]

    plaintext = transpose_encrypt(ciphertext, inverse)

    return plaintext
