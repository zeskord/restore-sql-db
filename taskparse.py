import argparse
import sys
import json

def create_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=str)
    return parser

def parse_task(filename = None):
    
    if filename == None:

        # Парсер параметров.
        parser = create_parser()
        arguments = parser.parse_args(sys.argv[1:])
        filename = arguments.data

    # Чтение входящих параметров.
    data = json.load(open(filename, encoding='utf-8'))
    return data[0]

def parse_from_text(text):
    data = json.loads(text)
    return data[0]