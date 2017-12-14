from reportlab.lib.pagesizes import letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4 , inch , landscape
from reportlab.platypus import SimpleDocTemplate , Table , TableStyle , Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io , datetime
from random import randint
from .schedular import main_schedule


def get_date_range(year , week):
    partial_date = "{0}-W{1}".format(year , week)
    date_1 = datetime.datetime.strptime(partial_date + '-1', "%Y-W%W-%w").strftime('%d, %b %Y')
    date_2 = datetime.datetime.strptime(partial_date + '-0', "%Y-W%W-%w").strftime('%d, %b %Y')

    return  date_1 + '-' + date_2

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


def gen_pdf_table(file_name , data , year , week):
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

    elements.append(Paragraph(' Generated schedule for year{0} , week {1}'.format(year,week) , p['title']))
    elements.append(Paragraph(' Effective date range for this period is {0}'.format(get_date_range(year , week)) , p['title']))

    elements.append(Paragraph('    ' , p['Normal']))

    # data2 = [[Paragraph(cell , s) for cell in row] for row in data]
    #
    # t = Table(data2)
    # t.setStyle(style)
    #
    # # Send the data and build the file
    # elements.append(t)
    line_text = ''
    for line in data:
        line_text = '' + line + line_text + '\r'

    elements.append(Paragraph(line_text,p['Normal']))
    doc.build(elements)
    save_file(file_name=file_name , buffer=buf)


def save_file(file_name , buffer):
    # Write the PDF to a file
    with open(file_name , 'wb') as fd:
        fd.write(buffer.getvalue())


def generate_sample_schedule():
    final_schedule = []

    names_er = ['Jennifer' , 'Lacey' , 'Voilet' , 'Nasim' , 'Carly' , 'Carrie' , 'Salma' ]
    names_opd = ['Jennifer' , 'Lacey' , 'Voilet' , 'Nasim' , 'Carly' , 'Carrie' , 'Salma']
    names_surg = ['Jennifer' , 'Lacey' , 'Voilet' , 'Nasim' , 'Carly' , 'Carrie' , 'Salma']


    days = ['Day1', 'Day2' , 'Day3' , 'Day4' , 'Day5' , 'Day6', 'Day7']

    wards = ['ER', 'OPD' , 'SURG']

    # schedule_header = "Ward:|Date:______|shift1__________________|shift2________________|shift3______________________ |"
    schedule_header = ['Ward' , 'Date' , 'shift1' , 'shift2' , 'shift3']

    final_schedule.append(schedule_header)
    schedule_line = " {0} : |{1}   |{2}  |{3}   |{4}"

    for ward in wards:
        for day in days:

            shift1 = names_opd[randint(0 , 6)] + '/' + names_er[randint(0 , 6)] + '/' + names_surg[randint(0 , 6)]
            shift2 = names_opd[randint(0 , 6)] + '/' + names_er[randint(0 , 6)] + '/' + names_surg[randint(0 , 6)]
            shift3 = names_opd[randint(0 , 6)] + '/' + names_er[randint(0 , 6)] + '/' + names_surg[randint(0 , 6)]

                # formated_schedule = schedule_line.format(ward , day , shift1 , shift2 , shift3)
            formated_schedule = [ward , day , shift1 , shift2 , shift3]
            final_schedule.append(formated_schedule)

    return final_schedule

def generate_real_schedule(year,week):
    capacity = 3
    data = main_schedule(year=year , week = week)

