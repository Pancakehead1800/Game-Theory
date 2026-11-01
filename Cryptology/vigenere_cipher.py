
from Cryptology.utils.cryptology import random_padding, index_of_coincidence, single_index_of_coincidence
from Cryptology.utils.number_theory import get_all_factors
from Cryptology.utils.constants import ENGLISH_FREQUENCIES
from collections import defaultdict

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



# ============ ATTACKING ============ #

# Apply frequency analysis to decrypt a shifted sequence of letters
def _find_caeser_shift(column):
        # run Chi-square for each column to find shift
        # use known english frequencies for expected
        best_shift = 0
        best_score = float('inf')

        for shift in range(26):
            decrypted = [(x - shift) % 26 for x in column]
            observed  = [decrypted.count(i) for i in range(26)]

            score = 0
            for i in range(26):
                expected = len(column) * ENGLISH_FREQUENCIES[i]
                score += (observed[i] - expected) ** 2 / expected

            if score < best_score:
                best_score = score
                best_shift = shift

        return best_shift

# for some ciphertext, we split it into n different columns
def _get_nth_sub_keys(ciphertext, key_length):
    columns = [[] for _ in range(key_length)]
    for i, x in enumerate(ciphertext):
        columns[i % key_length].append(x)
    return columns



def vigenere_kasiski_attack(ciphertext: list[int], seq_len=3):


    # ------ KASISKI METHOD ------ #
    
    # find the distances between repeated trigrams
    def find_repeat_distances(ciphertext, seq_len=seq_len):
        seq_indices = defaultdict(list)
        for i in range(len(ciphertext) - seq_len + 1):
            seq = tuple(ciphertext[i:i + seq_len])
            seq_indices[seq].append(i)

        distances = []
        for seq, indices in seq_indices.items():
            if len(indices) > 1:
                for j in range(len(indices) - 1):
                    distances.append(indices[j+1] - indices[j])

        return distances

    # find and sort factors of the distances
    def estimate_key_length(distances):
        factor_counts = defaultdict(int)

        for d in distances:
            for f in get_all_factors(d):
                factor_counts[f] += 1

        candidates = sorted(factor_counts.values(), reverse=True)

        return candidates

    # 1. find distances of repeated trigrams
    distances = find_repeat_distances(ciphertext)

    # 2. estimate key length
    candidates = estimate_key_length(distances)


    # ------ ESTIMATE KEY using most-likely key length ------ #
    # 3. split ciphertext to columns
    key_length = candidates[0]
    columns = _get_nth_sub_keys(ciphertext, key_length)

    # 4. determine likely key
    key = [_find_caeser_shift(col) for col in columns]

    return {
        "key_length": key_length,
        "key": key,
        "candidates": candidates
    }
    

def vigenere_shifted_coincidence_attack(ciphertext: list[int], lower_l=2, upper_l = 50, threshold = 0.060):

    # ------ SHIFTED COINCIDENCE METHOD ------ #
    def find_candidates(ciphertext):
        indices = defaultdict(float)
        for l in range(lower_l, min(upper_l, len(ciphertext)-1) + 1):
            x = ciphertext[:-l]
            y_l = ciphertext[l:]
            index = sum(a==b for a,b in zip(x, y_l)) / len(x)
            indices[l] = index

        candidates = {}
        for l, index in indices.items():
            if index >= threshold:
                candidates[l] = index
        candidates = sorted(candidates.values(), reverse=True)

    # 1. find candidates for key lengths
    candidates = find_candidates(ciphertext)

    # ------ ESTIMATE KEY using most-likely key length ------ #
    # 2. split ciphertext into columns
    key_length = candidates[0]
    columns = _get_nth_sub_keys(ciphertext, key_length)

    # 3. determine likely key
    key = [_find_caeser_shift(col) for col in columns]

    return {
        "key_length": key_length,
        "key": key,
        "candidates": candidates
    }
