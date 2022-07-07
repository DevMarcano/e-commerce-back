# -*- coding: UTF-8 -*
from pymongo import MongoClient
from django.conf import settings


class MongoORM:
	def __init__(self):
		self.mongo_user = settings.M_USER
		self.mongo_pwd = settings.M_PWD
		self.mongo_db = settings.M_DB
		self.mongo_host = settings.M_HOST
		self.mongo_port = int(settings.M_PORT)

	def Connect(self):
		string_conn = 'mongodb://%s:%s@%s:%d/%s'%(self.mongo_user, self.mongo_pwd, self.mongo_host, self.mongo_port, self.mongo_db)
		return MongoClient(string_conn)

	def Raw_Connect(self):
		return 'mongodb://%s:%s@%s:%d/%s'%(self.mongo_user, self.mongo_pwd, self.mongo_host, self.mongo_port, self.mongo_db)
		#return [self.mongo_user, self.mongo_pwd, self.mongo_host, self.mongo_port, self.mongo_db]

