

def transpose_encrypt(plaintext, k):
    plaintext = plaintext.lower()
    n = len(plaintext)
    ciphertext = ['A'] * n
    for i in range(n):
        if plaintext[i].isalpha():
            ciphertext[(i+k) % n] = plaintext[i].upper()
        else:
            ciphertext[(i+k) % n] = plaintext[i]
    return ''.join(ciphertext)

def transpose_decrypt(ciphertext, k=None, brute=False):

    # No helpful arguments given
    if k is None and brute == False:
        raise ValueError('Please enter a value for k or select the brute force option (ex: transpose_decrypt("abcde", k=5) or transpose_decrypt("abcde", brute=True)!')

    # k is not an integer:
    if not isinstance(k, int) and brute == False:
        raise ValueError(f'Make sure k={k} is an integer!')

    ciphertext = ciphertext.upper()

    # standard decryption where k is known
    if isinstance(k, int) and brute == False:
        n = len(ciphertext)
        plaintext = ['a'] * n
        for i in range(n):
            if ciphertext[i].isalpha():
                plaintext[(i-k) % n] = ciphertext[i].lower()
            else:
                plaintext[(i-k) % n] = ciphertext[i]
        return ''.join(plaintext)

    # brute force decryption
    if brute == True:
        decryptions = {}
        n = len(ciphertext)
        for i in range(n):
            plaintext = ["A"] * n
            for j in range(n):
                if ciphertext[j].isalpha():
                    plaintext[(j-i) % n] = ciphertext[j].lower()
                else:
                    plaintext[(j-i) % n] = ciphertext[i]
            plaintext = ''.join(plaintext).lower()
            decryptions[i] = plaintext
        return decryptions
