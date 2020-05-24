from mongoengine import *
from models import *

connect('pharmacy')


def load():
    with open('../resources/MNN.txt') as f:
        for l in f:
            mnn = MNN(name_ru=l.strip().upper())
            mnn.save()
            print(l.strip())


def clearfy():
    for mnn in MNN.objects().all():
        if mnn.name_ru[0] == ' ':
            print(mnn.name_ru)
            # mnn.name_ru = mnn.name_ru[:-1]
            # mnn.save()


if __name__ == '__main__':
    clearfy()