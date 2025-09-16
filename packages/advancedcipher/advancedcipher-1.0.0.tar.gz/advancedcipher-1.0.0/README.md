
# AdvancedCipher

مكتبة AdvancedCipher لتشفير النصوص باستخدام Caesar Cipher محسّن مع دعم الأرقام.

## الاستخدام

```python
from advancedcipher import encrypt, decrypt, auto_encrypt

msg = "Hello World 123"
enc = encrypt(msg, 3)
print("Encrypted:", enc)

dec = decrypt(enc, 3)
print("Decrypted:", dec)

auto, key = auto_encrypt(msg)
print("Auto Encrypted:", auto, "Key:", key)
