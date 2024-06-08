from engine.cryptography import encrypt, decrypt


def test_encryption_decryption():
    text = "Hello, world!"
    encrypted = encrypt(text)
    decrypted = decrypt(encrypted)
    assert text == decrypted