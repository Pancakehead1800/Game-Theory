
from affine_cipher import *
from shift_cipher import *
from transpose_cipher import *


plaintext = "this t3xt is to TE$t the Func1ion$! space...space "


# shift
a = shift_encrypt(plaintext, 5)
print(f"a={a}")

b = shift_decrypt(a, k=5, brute=True)
print(f"b={b}")


# tranpose
c = transpose_encrypt(plaintext, 5)
print(f"c={c}")

d = transpose_decrypt(c, 5)
print(f"d={d}")
