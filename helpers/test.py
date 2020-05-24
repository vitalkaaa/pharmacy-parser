from mongoengine import *
from models import *

connect('pharmacy')

r = Substance.objects(normative_documents__match={'number': 'ЛСР-000015/09-030816'}).all()
print(r)