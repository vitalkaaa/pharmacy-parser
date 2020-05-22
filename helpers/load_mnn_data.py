from mongoengine import *
from models import *

connect('pharmacy')

with open('../resources/MNN.txt') as f:
    for l in f:
        mnn = MNN(name_ru=l.strip().upper())
        mnn.save()
        print(l.strip())
