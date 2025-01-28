import csv


def read_csv(file_path: str) -> list:
    """
    Reads CSV file with Standardized Terms
    :param file_path: a path to csv file with standardized terms
    :return: a list with standardized terms in string format
    """
    standard_terms = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            standard_terms.append(row[0])
    return standard_terms


def read_txt(file_path: str) -> str:
    """
    Reads txt file with a text paragraph
    :param file_path: a path to txt document containing user input
    :return: a text from the file
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return lines[0]


def main():
    pass


if __name__ == '__main__':
    main()

