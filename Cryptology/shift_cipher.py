

def shift_encrypt(plaintext, k):
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

def shift_decrypt(ciphertext, k=None, brute=False):

    # No helpful arguments given
    if k is None and brute == False:
        raise ValueError('Please enter a value for k or select the brute force option (ex: shift_decrypt("abcde", k=5) or shift_decrypt("abcde", brute=True)!')

    # k is not an integer
    if not isinstance(k, int) and brute == False:
        raise ValueError(f'Make sure k={k} is an integer!')

    ciphertext = ciphertext.upper()

    # standard decryption where k is known
    if isinstance(k, int) and brute == False:
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

    # brute force decryption
    if brute == True:
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

    # something went wrong
    raise ValueError(f"Something went wrong: ciphertext={ciphertext}, k={k}, brute={brute}...")
