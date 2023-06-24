# File: AnimalShelter.py
# Date: 05-24-2023
# Author: Christopher Richards
# Email: christopher.richards4@snhu.edu

from pymongo import MongoClient
from bson.objectid import ObjectId
from os import environ
import warnings

class AnimalShelter(object):
    """Class for creating CRUD operations against a MongoDB database"""
    def __init__(self, user, password, host='nv-desktop-services.apporto.com', port=31580, db='AAC', collection='animals'):
        #Specify connection properties
        USER = user
        PASS = password
        HOST = host
        PORT = port
        DB = db
        COL = collection
        self.database = None
        self.collection = None
        self._lastException_ = None
        

        #Initialize client connection to MongoDB connection.
        try:
            self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER, PASS, HOST, PORT))
            self.database = self.client['%s' % (DB)]
            self.collection = self.database['%s' % (COL)]
        except Exception as e:
            print(str(e))
            return

    # Method for creating data on the MongoDB
    def create(self, data):
        #Check that data is not empty and that it is a dict
        if data is not None :
            if not isinstance(data, dict):
                raise Exception('Invalid data type. data of type %s must be of type <class \'dict\'>.' % type(data))
            if len(data) < 1:
                raise Exception('Parameter data may not be empty.')
            #insert data and retrieve the inserted_id. If it is None, insert unsuccessful.
            try:
                result_id = None
                result_id = self.collection.insert_one(data).inserted_id
                return result_id == None
            except Exception as e:
                self._lastException_ = str(e)
                return False
        else:
            raise Exception('Nothing to save, because data parameter is empty')

    #find the record specified by data.
    def read(self, data):
        #Check that data is not empty and that it is a dict
        if data is not None :
            if not isinstance(data, dict):
                raise Exception('Invalid data type. data of type %s must be of type <class \'dict\'>.' % type(data))
            try:
                fetch_data = self.collection.find(data, {'_id':False})
                #If length is greater than 0, return the fetched data, else return an empty list
                animals = []
                for animal in fetch_data:
                    animals.append(animal)
                return animals
            except Exception as e:
                self._lastException_ = str(e) + '\nTest!'
                return []

        else:
            raise Exception('Nothing to find, because data parameter is empty')
    
    #update documents that meet the find_criteria with the update_data provided
    def update(self, update_data, find_criteria={}):
        if update_data is None:
            raise Exception('Nothing to update because update_data parameter is empty')
        if find_criteria is None:
            raise Exception('Nothing to update because find_criteria parameter is empty')
        if not isinstance(update_data, dict):
            raise Exception('Invalid data type. update_data of type %s must be of type <class \'dict\'>.' % type(update_data))
        if not isinstance(find_criteria, dict):
            raise Exception('Invalid data type. find_criteria of type %s must be of type <class \'dict\'>.' % type(update_data))
        if len(update_data) < 1:
            raise Exception('update_data must have a length greater than 0.')
        if len(find_criteria) < 1:
            raise Exception('find_criteria must have a length greater than 0.')
        update_data = {
            '$set': update_data
        }
        
        try:
            modified_count = self.collection.update_many(find_criteria, update_data).modified_count
            return modified_count
        except Exception as e:
            self._lastException_ = str(e)
            return 0
    
    def delete(self, delete_criteria={}):
        if delete_criteria is None:
            raise Exception('Nothing to update because delete_criteria parameter is empty')
        if not isinstance(delete_criteria, dict):
            raise Exception('Invalid data type. delete_criteria of type %s must be of type <class \'dict\'>.' % type(delete_criteria))
        if len(delete_criteria) < 1:
            raise Exception('delete_criteria must have a length greater than 0.')
        try:
            deleted_count = self.collection.delete_many(delete_criteria).deleted_count
            return deleted_count
        except Exception as e:
            self._lastException_ = str(e)
            return 0