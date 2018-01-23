#!/usr/bin/env python3

from math import ceil
import sys

#given in super_cipher.py
#(after partially decrypting it)
def next(x):
    x = (x & 1) << N+1 | x << 1 | x >> N-1
    y = 0
    for i in range(N):
        y |= RULE[(x >> i) & 7] << i
    return y

#xors two byte arrays
def xor(bytes1, bytes2):
    return bytearray([(a ^ b) for (a, b) in zip(bytes1, bytes2)])

#decrypts as much as can be decrypted with the given key
def decrypt_some(key, input_bytes):
    return xor(key, input_bytes)

#gets the first N_BYTES of the keystream that was used
def get_base_keystream():
    return xor(txt, enc)[0:N_BYTES]

#gets the base keystream that was used, and generates the whole `length` byte keystream that can be used to decrypt
def generate_stream(length):
    keystream = get_base_keystream()
    curr_int = int.from_bytes(keystream, 'little')
    for i in range(ceil(length/N_BYTES) - 1):
        curr_int = next(curr_int)
        keystream += curr_int.to_bytes(N_BYTES, 'little')

    return keystream

#decrypts an array of bytes
def decrypt(input_bytes):
    length = len(input_bytes)
    keystream = generate_stream(length)
    return xor(input_bytes, keystream)

#takes in an int value of keystream, reverses the "prg" to get the value that came before it
def prev(y):
    #turn to bit string of 256 bits
    y = "{0:b}".format(y)
    y = y.zfill(N)

    #the last bit can be decoded as any of the 4 values of x that could have set that bit
    possibilities = dct[y[-1]]
    #loop in reverse to get all possible values of x that could have created this y
    for bit in reversed(y[:-1]):
        new_possibilities = []
        candidates = dct[bit]
        for candidate in candidates:
            for possibility in possibilities:
                #if the last 2 bits of the candidate match the first two bits of an existing possibility,
                #we can just append the first bit of the candidate to the possibility
                if candidate[1:] == possibility[:2]:
                    new_possibilities += [candidate[0] + possibility]
        possibilities = new_possibilities

    #Do some more checks to see which possibilities are actually valid
    real = []
    for possibility in possibilities:
        #the `next` function takes an input x, and turns it into x' such that the last bit of x' = the first bit of x, and the first bit of x' = the last bit of x
        #so check that the values of possibility are valid x' values in this way.
        if possibility[0] == possibility[-2]:
            if possibility[1] == possibility[-1]:
                real += [possibility]
    if len(real) != 1:
        print("there was an issue :(")
        print(len(real))
        sys.exit();

    #convert back to an int
    x = int(real[0], 2)

    #reverse the bit operations done in `next` 
    #(move the first bit to be the N'th bit, shift the rest of the value to the right by 1)
    x = ((x >> 1) & ((2**N) - 1)) | ((x & 1) << (N - 1))
    return x

#read the sample data given to us
txt = open("./sample_files/rule86.txt", "rb").read()
enc = open("./sample_files/rule86.txt.enc", "rb").read()
hint = open("./sample_files/hint.gif.enc", "rb").read()
py_file = open("./sample_files/super_cipher.py.enc", "rb").read()

#given in super_cipher.py
RULE = [(86 >> i) & 1 for i in range(8)]
N_BYTES = 32
N = 8 * N_BYTES

# in y = next(x), each 3 bits of x determines 1 bit of y
# use this dictionary to store this relation for reversing this function
dct = {
    #y      x
    "0" : ["000", "011", "101", "111"],
    "1" : ["001", "010", "100", "110"]
}

#we can get part of the key stream by just Xoring together a plaintext and a ciphertext
# C = (M ^ K), so C ^ M = K, which lets us recover the keystream.
partial_keystream = xor(txt, enc)

#use the partial key stream to get some partial outputs (lets us read most of the code file)
open("./outputs/hint_partial.gif", "wb").write(decrypt_some(partial_keystream, hint))
open("./outputs/super_cipher_partial.py", "wb").write(decrypt_some(partial_keystream, py_file))
open("./outputs/rule86_partial.txt", "wb").write(decrypt_some(partial_keystream, enc))

#generate the remainder of the keystream to decrypt full files
open("./outputs/super_cipher.py", "wb").write(decrypt(py_file))
open("./outputs/hint.gif", "wb").write(decrypt(hint))
open("./outputs/rule86.txt", "wb").write(decrypt(enc))

#At this point, we've decrypted the hint, which tells us to turn around, so we should try to reverse the "prg" to get the key that was input

#the first value of `keystream` used to encrypt the ciphertexts we've been given (the first 256 bits of the partial keystream)
base_key = int.from_bytes(partial_keystream[0:N_BYTES], 'little')

#use prev to reverse the key stream generation to get the original key
curr = base_key
for i in range(N//2):
    curr = prev(curr)
print(curr.to_bytes(N_BYTES, 'little'))
