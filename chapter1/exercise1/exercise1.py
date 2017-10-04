prefs = {
    'Pablo perez': {'sports', 'hockey', 'travelling', 'asia', 'morocco', 'programming', 'movies'},
    'Laura rodriguez': {'hockey', 'cooking', 'gambling', 'climbing', 'rafting', 'entrepreneur'},
    'Maria Masilla': {'hockey', 'sports', 'gambling', 'asia', 'programming', 'cooking'},
    'Alvaro Masilla': {'sports', 'sports', 'gambling', 'asia', 'programming', 'cooking'},
}


def sim_tanimato(prefs, person1, person2):
    intersection = [tag for tag in prefs[person1] if tag in prefs[person2]]
    union = prefs[person1].union(prefs[person2])
    return len(intersection) / float(len(union))


print sim_tanimato(prefs, "Pablo perez", "Maria Masilla")
print sim_tanimato(prefs, "Pablo perez", "Laura rodriguez")
print sim_tanimato(prefs, "Laura rodriguez", "Maria Masilla")
print sim_tanimato(prefs, "Maria Masilla", "Alvaro Masilla")
