
import random

def encrypt(text: str, shift: int) -> str:
    """تشفير النص باستخدام Caesar Cipher محسّن"""
    result = ""
    for char in text:
        if char.isupper():
            result += chr((ord(char) - 65 + shift) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) - 97 + shift) % 26 + 97)
        elif char.isdigit():
            result += chr((ord(char) - 48 + shift) % 10 + 48)
        else:
            result += char
    return result


def decrypt(text: str, shift: int) -> str:
    """فك التشفير"""
    return encrypt(text, -shift)


def auto_encrypt(text: str):
    """تشفير تلقائي مع مفتاح عشوائي"""
    shift = random.randint(1, 25)
    return encrypt(text, shift), shift

