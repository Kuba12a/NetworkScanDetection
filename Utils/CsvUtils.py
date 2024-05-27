import csv


def read_csv(file_path, delimiter):
    data = []

    with open(file_path, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_reader:
            data.append(row)

    return data
