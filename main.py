import json

from parsers import russian as rus_parser

from mongoengine import *
from models import *

connect(db='pharmacy')


def main():
    for mnn in MNN.objects().all():
        rus_parser.parse_substance(mnn)

    for mnn in MNN.objects().all():
        rus_parser.parse_medicine(mnn)


if __name__ == '__main__':
    main()
