import json

from parsers import russia as rus_parser

from mongoengine import *

connect(db='pharmacy')


def main():
    medicine_objects = dict()
    substance_object = dict()

    # for mnn in ['парацетамол']:
    #     medicine_objects[mnn] = rus_parser.parse_medicine(mnn)
    #     substance_object[mnn] = rus_parser.parse_substance(mnn)

    with open('output/medicine.json', 'w') as f:
        print(json.dumps(medicine_objects, indent=4, ensure_ascii=False), file=f)

    with open('output/substance.json', 'w') as f:
        print(json.dumps(substance_object, indent=4, ensure_ascii=False), file=f)


if __name__ == '__main__':
    main()
