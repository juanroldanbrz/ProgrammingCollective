import codecs
import csv

from tqdm import tqdm


def csv_unireader(f, encoding="utf-8"):
    for row in csv.reader(codecs.iterencode(codecs.iterdecode(f, encoding), "utf-8"), delimiter='\t'):
        try:
            data = [str(e.decode("utf-8")) for e in row]
            yield data
        except UnicodeEncodeError:
            pass


def get_bookmark_id_to_url_map(filename):
    filecsv = [line for line in csv_unireader(open(filename, 'r'), encoding='latin-1' )]
    id_url_map = {}
    for entry in filecsv[1:]:
        id_url_map[entry[0]] = entry[5].replace("www.", '')
    return id_url_map

def get_tag_id_to_tag_name_map(filename):
    filecsv = [line for line in csv_unireader(open(filename, 'r'), encoding='latin-1' )]
    id_url_map = {}
    for entry in filecsv[1:]:
        id_url_map[entry[0]] = entry[1]
    return id_url_map


def get_tag_to_tag_id_to_tag_weight(filename):
    filecsv = [line for line in csv_unireader(open(filename, 'r'), encoding='latin-1')]
    bookmark_id_to_tag_id_to_weight = {}
    for entry in filecsv[1:]:
        bookmark_id_to_tag_id_to_weight.setdefault(entry[0], {})
        bookmark_id_to_tag_id_to_weight[entry[0]][entry[1]] = entry[2]
    return bookmark_id_to_tag_id_to_weight


def generate_matrix_file(columns, rows, data, columns_name='Urls'):
    file = open("bookmark_matrix.csv", "w")
    file.write(columns_name)
    for column in columns.items():
        file.write('\t')
        file.write(column[1])

    for row in tqdm(rows.items()):
        row_id = row[0]

        if row_id in data.keys():
            file.write('\n')
            file.write(row[1])

            for column_id in columns:
                if column_id in data[row_id].keys():
                    file.write('\t' + data[row_id][column_id])
                else:
                    file.write('\t0')

    file.close()


if __name__ == "__main__":
    rows = get_bookmark_id_to_url_map('bookmarks.dat')
    columns = get_tag_id_to_tag_name_map('tags.dat')
    data = get_tag_to_tag_id_to_tag_weight('bookmark_tags.dat')

    generate_matrix_file(columns, rows, data)