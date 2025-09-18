# AdvancedCipherLib

مكتبة **AdvancedCipherLib** لتشفير النصوص باستخدام خوارزمية **Caesar Cipher** محسّنة مع دعم الأرقام، بالإضافة إلى دوال مساعدة للتشفير التلقائي.

---

##  المميزات
- تشفير وفك تشفير النصوص باستخدام **Caesar Cipher**.
- دعم الأرقام بجانب الحروف.
- توفير دالة **auto_encrypt** لتوليد مفتاح تلقائي وتجربة التشفير.

---

##  التثبيت
يمكن تثبيت المكتبة بعد رفعها على PyPI باستخدام:

```bash
pip install simple_advancedcipherlib
## الاستخدام
python
Copy code
from advancedcipher import encrypt, decrypt, auto_encrypt

msg = "Hello World 123"

# التشفير باستخدام مفتاح ثابت
enc = encrypt(msg, 3)
print("Encrypted:", enc)

# فك التشفير بنفس المفتاح
dec = decrypt(enc, 3)
print("Decrypted:", dec)

# التشفير التلقائي مع توليد مفتاح
auto, key = auto_encrypt(msg)
print("Auto Encrypted:", auto, "Key:", key)