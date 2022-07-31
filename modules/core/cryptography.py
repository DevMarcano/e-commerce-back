# -*- coding: UTF-8 -*
import urllib
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import base64

class AESCipher(object):
	def __init__(self, key): 
		self.bs = AES.block_size
		self.key = hashlib.sha256(key.encode()).digest()

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw.encode()))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

	def _pad(self, s):
		return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]

def make_hash(_params, _secret):
	sign = hashlib.md5()
	sign.update(_params + _secret)
	return sign.hexdigest()

def verify_hash(_remote, _params, _secret):
	sign = hashlib.md5()
	sign.update(_params.encode('utf-8') + _secret.encode('utf-8'))
	print(sign.hexdigest())
	return sign.hexdigest() == _remote


def encoded_params(dict_params):
	return urllib.quote(dict_params).encode('utf-8')

def encoded_dict(dict_params):
	return urllib.urlencode(dict_params).encode('utf-8')
