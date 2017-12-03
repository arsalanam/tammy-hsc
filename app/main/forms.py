from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')


class GenerateScheduleForm(Form):

    year = SelectField(
        'Year' , choices=[('2017' , '2017') , ('2018' , '2018') , ('2019' , '2019')] , validators=[Required()] )
    week = SelectField(
        'Week' , choices=[('1' , 'Week1') , ('2' , 'week2') , ('3' , 'Week3') ,
                          ('4' , 'Week4') , ('5' , 'week5') , ('6' , 'Week6') ,
                          ('7' , 'Week7') , ('8' , 'week8') , ('9' , 'Week9') ,
                          ('10' , 'Week10') , ('11' , 'week11') , ('12' , 'Week12') ,
                          ('13' , 'Week13') , ('14' , 'week14') , ('15' , 'Week15') ,
                          ('16' , 'Week16') , ('17' , 'week17') , ('18' , 'Week18') ,
                          ('19' , 'Week19') , ('20' , 'week20') , ('21' , 'Week21') ,
                          ('22' , 'Week22') , ('23' , 'week23') , ('24' , 'Week24') ,
                          ('25' , 'Week25') , ('26' , 'week26') , ('27' , 'Week27') ,
                          ('28' , 'Week28') , ('29' , 'week29') , ('30' , 'Week30') ,
                          ('31' , 'Week31') , ('32' , 'week32') , ('33' , 'Week33') ,
                          ('34' , 'Week34') , ('35' , 'week35') , ('36' , 'Week36') ,
                          ('37' , 'Week37') , ('38' , 'week38') , ('39' , 'Week39') ,
                          ('40' , 'Week40') , ('41' , 'week41') , ('42' , 'Week42') ,
                          ('43' , 'Week43') , ('44' , 'week44') , ('45' , 'Week45') ,
                          ('46' , 'Week46') , ('47' , 'week47') , ('48' , 'Week48') ,
                          ('49' , 'Week49') , ('50' , 'week50') , ('51' , 'Week51') ,
                          ('52' , 'Week52')

                          ] , validators=[Required()]


    )
    comments = PageDownField('Enter your comment')

    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')