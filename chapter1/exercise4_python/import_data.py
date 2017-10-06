import json
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)

movies = json.load(open('json/movies.json'))
ratings = json.load(open('json/ratings.json'))

client = MongoClient('localhost', 27017)
db = client.get_database('exercise1-4')

movies_collection = db.get_collection('movies')
rating_collection = db.get_collection('ratings')

movies_collection.insert(ratings)
logging.info('Inserted %d movies', len(movies))
rating_collection.insert(movies)
logging.info('Inserted %d ratings', len(ratings))
