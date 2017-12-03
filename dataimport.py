
from os.path import isfile , join , os
import csv
from app.models import db,  Ward
from  types import SimpleNamespace


basedir = os.path.abspath(os.path.dirname(__file__))
datadir = basedir + "/sample-data"


def import_ward(ward_file ):
    option_type_file = get_csv_file("wards")

    with open(option_type_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            datarow =  Ward( name= row[0], contact = row[1])

            db.session.add(datarow)
        db.session.commit




def get_csv_file(filename):

   return  join(datadir , filename + ".csv")





