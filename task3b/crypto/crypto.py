import random
import math


def is_prime(number):
    if number < 2:
        return False
    for i in range(2, number // 2 + 1):
        if number % i == 0:
            return False
    return True


def generate_prime(min_value, max_value):
    prime = random.randint(min_value, max_value)
    while not is_prime(prime):
        prime = random.randint(min_value, max_value)
    return prime


def mod_inverse(e, phi):
    for d in range(3, phi):
        if (d * e) % phi == 1:
            return d
    raise ValueError("Modular inverse does not exist")


# Generate two prime numbers p and q
p = generate_prime(1000, 10000)
q = generate_prime(1000, 10000)
while p == q:
    q = generate_prime(1000, 10000)

# Compute n and phi(n)
n = p * q
phi_n = (p - 1) * (q - 1)

# Choose e such that 1 < e < phi(n) and gcd(e, phi(n)) = 1
e = random.randint(3, phi_n - 1)
while math.gcd(e, phi_n) != 1:
    e = random.randint(3, phi_n - 1)

# Compute d, the modular inverse of e modulo phi(n)
d = mod_inverse(e, phi_n)

# Display the public and private keys
print(f"Public Key: (e={e}, n={n})")
print(f"Private Key: (d={d}, n={n})")
print(f"Phi of n: {phi_n}")

# Get the message to be encrypted and decrypted from the user
message = input("Enter a message to be encrypted: ")

# Encrypt the message
message_encoded = [ord(char) for char in message]
ciphertext = [pow(char, e, n) for char in message_encoded]
print(f"Ciphertext: {ciphertext}")

# Decrypt the message
message_decoded = [pow(char, d, n) for char in ciphertext]
decrypted_message = ''.join(chr(char) for char in message_decoded)
print(f"Decrypted Message: {decrypted_message}")

# Signing a message


def sign_message(private_key, message):
    d, n = private_key
    message_encoded = [ord(char) for char in message]
    signature = [pow(char, d, n) for char in message_encoded]
    return signature

# Verifying a signature


def verify_signature(public_key, message, signature):
    e, n = public_key
    message_encoded = [ord(char) for char in message]
    decoded_signature = [pow(char, e, n) for char in signature]
    return message_encoded == decoded_signature


# Get the message to be signed and verified from the user
message_to_sign = input("Enter a message to be signed: ")

# Sign the message using the private key
signature = sign_message((d, n), message_to_sign)
print(f"Signature: {signature}")

# Verify the signature using the public key
is_valid = verify_signature((e, n), message_to_sign, signature)
print(f"Signature valid: {is_valid}")
