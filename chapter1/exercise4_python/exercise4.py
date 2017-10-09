from pymongo import MongoClient
import logging
from sortedcontainers import SortedListWithKey

logging.basicConfig(level=logging.INFO)

client = MongoClient('localhost', 27017)
db = client.get_database('exercise1-4')

movies_collection = db.get_collection('movies')
rating_collection = db.get_collection('ratings')


def sim_distance(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    # if they have no ratings in common, return 0
    if len(si) == 0:
        return 0
    # Add up the squares of all the differences
    sum_of_squares = sum(
        [pow(prefs[person1][item] - prefs[person2][item], 2) for item in prefs[person1] if item in prefs[person2]])
    return 1 / (1 + sum_of_squares)


def precompute_similar_person(prefs):
    logging.info("Computing similar persons")
    similar_users_map = dict([user_id, SortedListWithKey(key=lambda x: -x[1])] for user_id in prefs)

    for user_id in similar_users_map:
        for user_id_to_compare in prefs:
            if user_id_to_compare != user_id:
                similar_users_map[user_id].add((user_id_to_compare, sim_distance(prefs, user_id, user_id_to_compare)))

    return similar_users_map


def get_recommendations(prefs, persons_with_persons_similitude_dict, top=5):
    recommendations_for_user = {}

    for person in persons_with_persons_similitude_dict:
        tmp_movie_score = {}
        for similar_person in persons_with_persons_similitude_dict[person][:top]:
            similar_person_name = similar_person[0]
            for movie in prefs[similar_person_name]:
                if movie not in prefs[person]:
                    if movie not in tmp_movie_score:
                        tmp_movie_score[movie] = {'total_score': 0, 'weigh': 0.0}
                    tmp_movie_score[movie]['weigh'] += similar_person[1]
                    tmp_movie_score[movie]['total_score'] += similar_person[1] * prefs[similar_person_name][movie]

        tmp_movie_score = [(movie[0], movie[1]['total_score'] / movie[1]['weigh']) for movie in tmp_movie_score.items()
                           if movie[1]['total_score'] != 0]
        recommendations_for_user[person] = tmp_movie_score

    for user_id in recommendations_for_user:
        list_of_ratings = SortedListWithKey(key=lambda x: -x[1])
        for touple in recommendations_for_user[user_id]:
            list_of_ratings.add( (touple[0], touple[1]))
        recommendations_for_user[user_id] = list_of_ratings
    return recommendations_for_user


def get_user_id_rating_map():
    user_id_list = rating_collection.find({}).distinct('userId')
    user_id_rating_map = dict()
    for user_id in user_id_list:
        user_id_rating_map[user_id] = dict()
        movies_rated_by_user = rating_collection.find({'userId' : user_id})
        for movie_rated in movies_rated_by_user:
            user_id_rating_map[user_id][movie_rated['movieId']] = float(movie_rated['rating'])
    return user_id_rating_map

user_id_rating = get_user_id_rating_map()
similar_person = precompute_similar_person(user_id_rating)
recommendations = get_recommendations(user_id_rating, similar_person, 6)
