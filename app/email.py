from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg ):
    with app.app_context():
        mail.send(msg)


def send_email_with_attachment(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])

    _week = kwargs['week']
    _year =  kwargs['year']
    _date_range= kwargs['date_range']
    _custom_message = kwargs['message']

    file_name = 'week' + str(_week) + '.pdf'

    file_path = 'data/' + file_name

     #pdf_path = 'app/' + file_path

    msg.body = render_template(template + '.txt' , **kwargs)
    msg.html = render_template(template + '.html' , **kwargs)

    with app.open_resource(file_path) as fp:
        msg.attach(file_path ,"application/pdf" , fp.read())
    thr = Thread(target=send_async_email, args=[app, msg  ])
    thr.start()
    return thr

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email , args=[app , msg])
    thr.start()
    return thr
