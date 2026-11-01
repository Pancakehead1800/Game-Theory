

def shift_encrypt(plaintext, k):
    # standard encryption
    plaintext = plaintext.lower()
    ciphertext = ""
    for char in plaintext:
        if char.isalpha():
            encoding = ord(char) - ord('a')
            shifted = (encoding + k) % 26
            ciphertext += chr(shifted + ord('a'))
        else:
            ciphertext += char
    ciphertext = ciphertext.upper()
    return ciphertext


def shift_decrypt(ciphertext, k):
    # standard decryption 
    ciphertext = ciphertext.upper()
    plaintext = ""
    for char in ciphertext:
        if char.isalpha():
            encoding = ord(char) - ord('A')
            shifted = (encoding - k) % 26
            plaintext += chr(shifted + ord('A'))
        else:
            plaintext += char

    plaintext = plaintext.lower()
    return plaintext


def shift_brute_decrypt(ciphertext):
    # standard decryption, but as a brute
    decryptions = {}
    for i in range(26):
        plaintext = ""
        for char in ciphertext:
            if char.isalpha():
                encoding = ord(char) - ord('A')
                shifted = (encoding - i) % 26
                plaintext += chr(shifted + ord('A'))
            else:
                plaintext += char
        plaintext = plaintext.lower()
        decryptions[i] = plaintext
    return decryptions
