import json

from parsers import russian as rus_parser

from mongoengine import *
from models import *

connect(db='pharmacy')


def main():
    medicine_objects = dict()
    substance_object = dict()

    for mnn in MNN.objects(name_ru='ПАРАЦЕТАМОЛ').all():
        rus_parser.parse_medicine(mnn)
    #     rus_parser.parse_substance(mnn)

    # with open('output/medicine.json', 'w') as f:
    #     print(json.dumps(medicine_objects, indent=4, ensure_ascii=False), file=f)
    #
    # with open('output/substance.json', 'w') as f:
    #     print(json.dumps(substance_object, indent=4, ensure_ascii=False), file=f)


if __name__ == '__main__':
    main()
