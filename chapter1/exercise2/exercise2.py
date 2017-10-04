import csv
import string

from tqdm import tqdm


def sim_tanimato(str1, str2):
    if len(str1) > len(str2):
        char_array_longer_str = list(str1)
        char_array_shorter_str = list(str2)
    else:
        char_array_shorter_str = list(str1)
        char_array_longer_str = list(str2)

    shorter_length = len(char_array_shorter_str)

    intersection = []
    union = []

    for idx, char in enumerate(char_array_longer_str):
        if idx < shorter_length:
            union.append(char)

            if char == char_array_shorter_str[idx]:
                intersection.append(char)
            else:
                union.append(char_array_shorter_str[idx])
        else:
            union.append(char)

    if len(intersection) == 0:
        return 0
    else:
        return len(intersection) / float(len(union))


def parse_dat(filename):
    printable = set(string.printable)
    raw_data = open(filename, 'rt')
    reader = csv.reader(raw_data, delimiter=',', quoting=csv.QUOTE_NONE)
    parsed_dat = [value[1] for value in list(reader)]
    return [filter(lambda x: x in printable, str(ele).decode('utf-8', 'ignore')) for ele in parsed_dat]


def calculate_similar_words(tags, min_sim_rate=0.86):
    similar_words = []
    pbar = tqdm(total=len(tags))

    for idx, tag in enumerate(tags):
        pbar.update(1)
        pbar.set_description("Testing similar tags to " + tag)
        for tag_to_compare in tags[idx + 1:]:
            tanimato_rate = sim_tanimato(tag, tag_to_compare)
            if tanimato_rate > min_sim_rate:
                similar_words.append({tag, tag_to_compare, tanimato_rate})
    return similar_words


def calculate_words_similar_to_target(tags, target, min_sim_rate=0.85):
    similar_words = []
    for tag in tags:
        tanimato_rate = sim_tanimato(target, tag)
        if tanimato_rate > min_sim_rate:
            similar_words.append({target, tag, tanimato_rate})
            print(target, tag, tanimato_rate)
    return similar_words


tags = parse_dat('tags.dat')

# Calculate similar words
print calculate_similar_words(tags, 0.90)
# print calculate_words_similar_to_target(tags, "programming")
