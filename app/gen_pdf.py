from reportlab.lib.pagesizes import letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4 , inch , landscape
from reportlab.platypus import SimpleDocTemplate , Table , TableStyle , Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
from random import randint

def generate_pdf(file_name , pdf_data):
    buf = io.BytesIO()

    # Setup the document with paper size and margins
    doc = SimpleDocTemplate(
        buf ,
        rightMargin=inch / 2 ,
        leftMargin=inch / 2 ,
        topMargin=inch / 2 ,
        bottomMargin=inch / 2 ,
        pagesize=letter ,
    )

    # Styling paragraphs
    styles = getSampleStyleSheet()

    # Write things on the document
    paragraphs = []
    for item in pdf_data:
        paragraphs.append(
            Paragraph(item , styles['Normal']))

    doc.build(paragraphs)
    save_file(file_name=file_name , buffer=buf)


def gen_pdf_table(file_name , data):
    buf = io.BytesIO()

    doc = SimpleDocTemplate(buf , pagesize=A4 , rightMargin=30 , leftMargin=30 , topMargin=30 ,
                            bottomMargin=18)
    doc.pagesize = landscape(A4)
    elements = []


    # TODO: Get this line right instead of just copying it from the docs
    style = TableStyle([('ALIGN' , (1 , 1) , (-2 , -2) , 'RIGHT') ,
                        ('TEXTCOLOR' , (1 , 1) , (-2 , -2) , colors.red) ,
                        ('VALIGN' , (0 , 0) , (0 , -1) , 'TOP') ,
                        ('TEXTCOLOR' , (0 , 0) , (0 , -1) , colors.blue) ,
                        ('ALIGN' , (0 , -1) , (-1 , -1) , 'CENTER') ,
                        ('VALIGN' , (0 , -1) , (-1 , -1) , 'MIDDLE') ,
                        ('TEXTCOLOR' , (0 , -1) , (-1 , -1) , colors.green) ,
                        ('INNERGRID' , (0 , 0) , (-1 , -1) , 0.25 , colors.black) ,
                        ('BOX' , (0 , 0) , (-1 , -1) , 0.25 , colors.black) ,
                        ])

    # Configure style and word wrap
    s  = getSampleStyleSheet()
    p = s
    s = s["BodyText"]
    s.wordWrap = 'CJK'

    elements.append(Paragraph('A Sample Fake schedule generated via random names' , p['title']))

    elements.append(Paragraph('    ' , p['Normal']))

    data2 = [[Paragraph(cell , s) for cell in row] for row in data]

    t = Table(data2)
    t.setStyle(style)

    # Send the data and build the file
    elements.append(t)
    doc.build(elements)
    save_file(file_name=file_name , buffer=buf)


def save_file(file_name , buffer):
    # Write the PDF to a file
    with open(file_name , 'wb') as fd:
        fd.write(buffer.getvalue())


def generate_sample_schedule():
    final_schedule = []

    names_general = ['Shamin' , 'Nasreen' , 'Naseem' , 'Khalida' , 'Majida' , 'Naeema' , 'Nasim' , 'Ayesha' ,
                     'Khadija' , 'Hajira' , 'Nabeela' , 'Amreen' , 'Adeela' , 'Arshi' , 'Azra' , 'Durdana' ,
                     'Kehkeshan' , 'Majeedan' , 'Khatoon' , 'Fairy' , 'Raheela' , 'Sajida' , 'Shaeena' , 'Nagmana' ,
                     'Tahira']
    names_ot = ['Asma' , 'Zainab' , 'Alaya' , 'Naveed' , 'Ahmed' , 'Aslam' , 'Labeeb' , 'Kalid' , 'Nasir' , 'Aamina' ,
                'Mamoona' , 'Maihra']
    names_er = ['Mary' , 'Nancy' , 'Jennifer' , 'Adam' , 'Lacie' , 'Katie' , 'Cody' , 'Lina' , 'Katrina' , 'Irena' ,
                'Farina']
    names_peads = ['Kim' , 'Jamie' , 'Carrie' , 'Amy' , 'Annie' , 'Nikki' , 'Christy' , 'Tammra' , 'Jim' , 'Brian' ,
                   'Ashima']

    days = ['02, Jan 2017' , '03, Jan 2017' , '04, Jan 2017' , '05, Jan 2017' , '06, Jan 2017' , '07, Jan 2017' ,
            '08, Jan 2017']

    wards = ['ER' , 'OT' , 'PEAD' , 'OPD']

    # schedule_header = "Ward:|Date:______|shift1__________________|shift2________________|shift3______________________ |"
    schedule_header = ['Ward' , 'Date' , 'shift1' , 'shift2' , 'shift3']

    final_schedule.append(schedule_header)
    schedule_line = " {0} : |{1}   |{2}  |{3}   |{4}"

    for ward in wards:
        for day in days:

            if ward == 'ER':
                shift1 = names_er[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                    randint(1 , 20)]
                shift2 = names_er[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                    randint(1 , 20)]
                shift3 = names_er[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                    randint(1 , 20)]

                # formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                formated_schedule = [ward , day , shift1 , shift2 , shift3]
                final_schedule.append(formated_schedule)
            if ward == 'OT':
                shift1 = names_ot[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                    randint(1 , 20)]
                shift2 = names_ot[randint(1 , 10)] + '/' + names_general[randint(1 , 20)]
                shift3 = names_ot[randint(1 , 10)] + '/' + names_general[randint(1 , 20)]
                # formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                formated_schedule = [ward , day , shift1 , shift2 , shift3]
                final_schedule.append(formated_schedule)
            if ward == 'PEAD':
                shift1 = names_peads[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                    randint(1 , 20)]
                shift2 = names_peads[randint(1 , 10)] + '/' + names_general[randint(1 , 20)]
                shift3 = names_peads[randint(1 , 10)] + '/' + names_general[randint(1 , 20)]
                # formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                formated_schedule = [ward , day , shift1 , shift2 , shift3]
                final_schedule.append(formated_schedule)
            else:
                shift1 = names_general[randint(1 , 10)] + '/' + names_general[randint(1 , 20)] + '/' + names_general[
                    randint(1 , 20)]
                shift2 = names_general[randint(1 , 10)]
                shift3 = names_general[randint(1 , 10)]
                # formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
                formated_schedule = [ward , day , shift1 , shift2 , shift3]
                final_schedule.append(formated_schedule)

    return final_schedule
