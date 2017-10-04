from sortedcontainers import SortedListWithKey

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


# Returns a distance-based similarity score for person1 and person2
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
    similar_persons_map = dict([person, SortedListWithKey(key=lambda x: -x[1])] for person in prefs)

    for person in similar_persons_map:
        for person_to_compare in prefs:
            if person_to_compare != person:
                similar_persons_map[person].add((person_to_compare, sim_distance(prefs, person, person_to_compare)))

    return similar_persons_map

def get_recommendations(prefs, persons_with_persons_similitude_dict, top=5):
    recommendations_for_user = dict([person, ()] for person in prefs)

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
    return recommendations_for_user


if __name__ == "__main__":
    similitude = precompute_similar_person(critics)
    print get_recommendations(critics, similitude)
