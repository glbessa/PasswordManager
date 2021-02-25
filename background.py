import os
import sqlite3
import random
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305


class Crypto():
	def encrypt_ChaChaPoly(key=ChaCha20Poly1305.generate_key(), data:bytes, nonce=os.urandom(12), associated_data=None):
		chacha = ChaCha20Poly1305(key)
		encrypted_data = chacha.encrypt(nonce, data, associated_data)

		return key, encrypted_data, nonce, associated_data

	def decrypt_ChaChaPoly(key:bytes, encrypted_data:bytes, nonce:bytes, associated_data=None):
		chacha = ChaCha20Poly1305(key)
		data = chacha.decrypt(nonce, data, associated_data)

		return data

	def encrypt_AESGCM(key:bytes, data:bytes, nonce:bytes, associated_data:bytes):
		if key == None:
			key = AESGCM.generate_key(256)
			aesgcm = AESGCM(key)
			encrypted_data = aesgcm.encrypt(nonce, data, associated_data)

			return key, encrypted_data

		else:
			aesgcm = AESGCM(key)
			encrypted_data = aesgcm.encrypt(nonce, data, associated_data)

			return encrypted_data

	def decrypt_AESGCM(key:bytes, encrypted_data:bytes, nonce:bytes, associated_data=None):
		aesgcm = AESGCM(key)
		data = aesgcm.decrypt(nonce, encrypted_data, associated_data)

		return data

	def sha3_256(data:bytes):
		_hash = hashlib.sha3_256()
		_hash.update(data)

		return _hash.digest()

class Intermediary():
	'''
		META FORMAT:
		{
			'creation_time': ******,
			'modified_time': *****,
			'last_read_time': ******,
			'key_sha3': ****,
			'nonce': nonce,
			'associated_path': associated_path
		}

		CONTENT FORMAT:
		{
			'id':{
				'user': *****,
				'password': *****,
				'obs': ******, 
			},

			...
		}
	'''

	def __init__(self, db:str, key:bytes, associated_data=b'':bytes):
		if os.path.exists(db):
			self.load_meta(db, key)
		else:
			self.db = db
			self.creation_time = datetime.now()
			self.modified_time = datetime.now()
			self.last_read_time = datetime.now()			
			self.key_hash = Crypto.sha3_256(key)
			self.nonce = os.urandom(12)
			self.associated_data = associated_data
			self.data = {}
 
	def create_meta(self, key:bytes):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()

			cursor.execute('''
					CREATE TABLE metadata (
						creation_time TEXT NOT NULL,
						modified_time TEXT NOT NULL,
						last_read_time TEXT NOT NULL,
						key_sha3 BLOB NOT NULL,
						nonce BLOB NOT NULL,
						associated_data BLOB NOT NULL
					)
				''')

			cursor.execute('INSERT INTO metadata (creation_time, modified_time, last_read_time, key_sha3, nonce, associated_data) VALUES (?, ?, ?, ?, ?, ?)', (self.creation_time.isoformat(' '), self.modified_time.isoformat(' '), self.last_read_time.isoformat(' '), Crypto.encrypt_AESGCM(key, self.key_hash, self.nonce, self.), self.nonce, self.associated_data))

			connection.commit()

			cursor.close()

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def create_data(self):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()
			cursor.execute('''
					CREATE TABLE data (
						index INTEGER PRIMARY KEY AUTOINCREMENT,
						application BLOB,
						user BLOB,
						password BLOB NOT NULL,
						obs BLOB
					)
				''')

			connection.commit()

			cursor.close()

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def load_meta(self, key:bytes):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()
			cursor.execute('SELECT * FROM metadata')

			result = cursor.fetchone()[0]

			self.creation_time = datetime.fromisoformat(result[0])
			self.modified_time = datetime.fromisoformat(result[1])
			self.last_read_time = datetime.fromisoformat(result[2])
			self.nonce = result[4]
			self.associated_data = result[5]
			self.key_hash = Crypto.decrypt_AESGCM(key, result[3], self.nonce, self.associated_data)

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def load_data(self, key:bytes):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()
			cursor.execute('SELECT * FROM data')

			result = cursor.fetchall()

			cursor.close()

			for row in result:
				_data = {
					row[0]: {
						'application':Cripto.decrypt_AESGCM(key, row[1], self.nonce, self.associated_data),
						'user':row[2],
						'password':row[3],
						'obs':row[4]
					}
				}

				data.update(_data)

			del(key)

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def insert_data(self, key:bytes, application:str, user:str, password:str, obs:str):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()

			cursor.execute('INSERT INTO data (application, user, password, obs) VALUES (?, ?, ?, ?)', self.encrypt_row(key, application, user, password, obs))

			connection.commit()

			cursor.close()

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def update_data(self, key:bytes, index:int, **items):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()

			for _key, _value in items.items():
				cursor.execute('UPDATE data SET ? = ? WHERE index = ?', (_key, self.encrypt_item(key, _value), index))

			connection.commit()

			cursor.close()

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def delete_data(self, key:bytes, index:int):
		try:
			connection = sqlite3.connect(self.db)
			cursor = connection.cursor()

			cursor.execute('DELETE FROM data WHERE index = ?', (index, ))

			connection.commit()

			cursor.close()

		except Exception as ex:
			raise ex

		finally:
			connection.close()

	def view_data(self, key:bytes, index:int):


	def encrypt_item(self, key, item):
		return Crypto.encrypt_AESGCM(key, item.encode(), self.nonce, self.associated_data)

	def encrypt_row(self, key, application, user, password, obs):
		application = self.encrypt_item(key, application)
		user = self.encrypt_item(key, user)
		password = self.encrypt_item(key, password)
		obs = self.encrypt_item(key, obs)

		del(key)

		return (application, user, password, obs)

	def check_key(key:bytes, func):
		_hash = Crypto.sha3_256(key)
		if self.key_hash == _hash
			return True
		else:
			return False



#class Metadata():
#	def __init__(self, content_file, nonce, associated_data):
#		self.file_path = content_file
#		self.nonce = nonce
#		self.associated_data = associated_data

#class Senha():
#	def __init__(self, id, user, password, obs):
#		self.id = id
#		self.user = user
#		self.password = password
#		self.obs = obs
