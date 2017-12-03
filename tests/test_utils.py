import unittest

from flask import current_app
from app import create_app, db

from app.gen_pdf import generate_pdf , gen_pdf_table
from random import randint

class PdfTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_prd_gen(self):

        file_name = 'app/data/week53.pdf'
        pdf_data =   self.gen_schedule()


        gen_pdf_table(file_name=file_name , data= pdf_data)


    def gen_schedule(self):

        final_schedule = []

        names_general = ['Shamin' , 'Nasreen' , 'Naseem' , 'Khalida' , 'Majida' , 'Naeema' , 'Nasim' , 'Ayesha' ,
                         'Khadija' , 'Hajira' , 'Nabeela' , 'Amreen' , 'Adeela' , 'Arshi' , 'Azra' , 'Durdana' ,
                         'Kehkeshan' , 'Majeedan' , 'Khatoon' , 'Fairy' , 'Raheela' , 'Sajida' , 'Shaeena' , 'Nagmana' , 'Tahira']
        names_ot = ['Asma' , 'Zainab' , 'Alaya' , 'Naveed' , 'Ahmed' , 'Aslam', 'Labeeb' , 'Kalid' , 'Nasir' , 'Aamina' , 'Mamoona' , 'Maihra']
        names_er = ['Mary' , 'Nancy' , 'Jennifer' , 'Adam' , 'Lacie' , 'Katie' , 'Cody' , 'Lina' , 'Katrina' , 'Irena' , 'Farina']
        names_peads = ['Kim' , 'Jamie' , 'Carrie' , 'Amy' , 'Annie' , 'Nikki' , 'Christy' , 'Tammra' , 'Jim' , 'Brian' , 'Ashima' ]

        days = ['02, Jan 2017' , '03, Jan 2017' , '04, Jan 2017' , '05, Jan 2017' , '06, Jan 2017' , '07, Jan 2017' ,
                '08, Jan 2017']

        wards = ['ER' , 'OT' , 'PEAD' , 'OPD']



        #schedule_header = "Ward:|Date:______|shift1__________________|shift2________________|shift3______________________ |"
        schedule_header = ['Ward' , 'Date' , 'shift1' , 'shift2' , 'shift3']

        final_schedule.append(schedule_header)
        schedule_line   = " {0} : |{1}   |{2}  |{3}   |{4}"

        for ward in wards:
            for day in days:

                if ward =='ER':
                    shift1 = names_er[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' +  names_general[randint(1 , 20)]
                    shift2 = names_er[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift3 = names_er[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]

                     #formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                    formated_schedule= [ward , day , shift1 , shift2 , shift3]
                    final_schedule.append(formated_schedule)
                if ward == 'OT':
                    shift1 = names_ot[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift2 = names_ot[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift3 = names_ot[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    #formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                    formated_schedule= [ward , day , shift1 , shift2 , shift3]
                    final_schedule.append(formated_schedule)
                if ward == 'PEAD':
                    shift1 = names_peads[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift2 = names_peads[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift3 = names_peads[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    #formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                    formated_schedule =[ward , day , shift1 , shift2 , shift3]
                    final_schedule.append(formated_schedule)
                else:
                    shift1 = names_general[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift2 = names_general[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    shift3 = names_general[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                        randint(1 , 20)]
                    #formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                    formated_schedule=[ward , day , shift1 , shift2 , shift3]
                    final_schedule.append(formated_schedule)








        return final_schedule








