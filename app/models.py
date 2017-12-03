from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property
from app.exceptions import ValidationError
from . import db, login_manager
import enum





wardrequirements = db.Table(
    'ward_requirements',
    db.Column('ward_id', db.Integer, db.ForeignKey('ward.id')),
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirement.id'))
)






class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))



    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def create_admin():
        from sqlalchemy.exc import IntegrityError

        u = User(email="arsalanam@yahoo.com",
                 username="admin",
                 password="Admin123",
                 confirmed=True,
                 name="Admin",
                 location="SFO",
                 about_me="IPSUM LORUM")
        role = Role.query.filter_by(name='Administrator').first()
        if role:
            u.role = role

        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()



    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Ward(db.Model):
    __tablename__= "ward"
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    name = db.Column(db.String(255) , unique=True , nullable=False)
    contact = db.Column(db.String(255) , nullable=False)
    phone = db.Column(db.String(255) , nullable=False)
    requirements = db.relationship(
        'Requirement',
        secondary=wardrequirements,
        backref=db.backref('WardRequirement', lazy='dynamic')
    )

    def __init__(self , name = None , contact = None , phone = None ):
        self.name = name
        self.contact = contact
        self.phone = phone

    def __repr__(self):
        return '<Ward {0}>'.format(self.name)

    @hybrid_property
    def requirements_list(self):
        names = self.requirements

        return names


class Requirement(db.Model):
    __tablename__ = "requirement"
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    name = db.Column(db.String(255) , unique=False , nullable=True)
    requirement_type = db.Column(db.Enum("WEEKDAY" , "WEEKEND"))
    skill_id = db.Column(db.Integer , db.ForeignKey('skills.id'))
    skill=db.relationship('Skill',uselist=False)
    min_num_staff_s0 = db.Column(db.Integer , default = 0 , nullable=True)
    min_num_staff_s1 = db.Column(db.Integer , default=0 , nullable=True)
    min_num_staff_s2 = db.Column(db.Integer , default=0 , nullable=True)

    def __init__(self , name = None, requirement_type = None  ):
       self.name = name
       self.requirement_type = requirement_type



    def __repr__(self):
        return '< requirmenent {0}>'.format(self.name)






class Nurse(db.Model):
    __tablename__= "nurse"
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)

    first_name=db.Column(db.String(255),unique=False,nullable=False)
    last_name=db.Column(db.String(255),unique=False,nullable=False)
    age=db.Column(db.Integer,unique=False,nullable=False)
    gender = db.Column(db.Enum("MALE" , "FEMALE"))

    salutation = db.Column(db.Enum("Mr" , "Ms" , "Mrs." , "Dr" , "Madam" , "Sir" ))
    tribal_name = db.Column(db.String(255),nullable=True)
    address=db.Column(db.String(255),nullable=False)
    address2=db.Column(db.String(255),nullable=True)
    city = db.Column(db.String(255) , nullable=False , default = "city")
    province=db.Column(db.String(255),nullable=False)

    postal_code=db.Column(db.String(255),nullable=False)
    skills = db.relationship('NurseSkills', backref='nurse')
    vacations=db.relationship('NurseVacations', backref='nurse')


    def __init__(self,first_name =None,last_name =None,age=None, gender=None,salutation = None , address=None,
                 address2=None,province=None,postal_code=None):
        self.first_name=first_name
        self.last_name=last_name
        self.age=age
        self.gender=gender
        self.salutation = salutation
        self.address=address
        self.address2=address2
        self.province=province
        self.postal_code=postal_code
    def __repr__(self):
        return '<{2}  {1} , {0}>'.format( self.last_name , self.first_name , self.salutation )

class NurseSkills(db.Model):

    __tablename__="nurse_skills"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skill_id = db.Column(db.Integer , db.ForeignKey('skills.id'))
    skill=db.relationship('Skill',uselist=False)
    description=db.Column(db.String(255),nullable=True)
    years_of_experience=db.Column(db.Integer,nullable=False)
    active=db.Column(db.Boolean,nullable=False)
    nurse_id=db.Column(db.Integer,db.ForeignKey('nurse.id'))


    def __init__(self,skill = None,description = None,years_of_experience = 0,active = True):
        self.skill=skill
        self.description=description
        self.years_of_experience=years_of_experience
        self.active=active

    def __repr__(self):
        return '<Nurse Skill {0} exp {1}>'.format(self.skill , self.years_of_experience)

class NurseVacations(db.Model):

    __tablename__="nurse_vacations"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description=db.Column(db.String(255),nullable=True)
    vacation_start_date=db.Column(db.DateTime , nullable=True)
    vacation_end_date = db.Column(db.DateTime , nullable=True )
    nurse_id=db.Column(db.Integer,db.ForeignKey('nurse.id'))


    def __init__(self,description = None,vacation_start_date=None ,vacation_end_date=None):

        self.description=description
        self.vacation_start_date=vacation_start_date
        self.vacation_end_date=vacation_end_date

    def __repr__(self):
        return '<Nurse vacations >'


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    skill = db.Column(db.String(255) , unique=True , nullable=True)
    description = db.Column(db.String(255) , nullable=True)



    def __init__(self , skill=None , description = None):
        self.skill=skill
        self.description = description

    def __repr__(self):
        return '<Skill {0} >'.format(self.skill)




class GeneratedSchedule(db.Model):
    __tablename__ = "generated_schedule"
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    generated_by = db.Column(db.String(255) ,  nullable=True)
    week = db.Column(db.Integer , nullable=False)
    year= db.Column(db.Integer , nullable=False , default= 2017)
    date_generated =  db.Column(db.DateTime, index=True, default=datetime.utcnow)
    file_name = db.Column(db.String(255) , nullable=False )
    comments = db.Column(db.String(255) , nullable=True )

    def __init__(self , generated_by=None , week = None , year = None , date_generated = None ,
                 file_name = None , comments = None):
        self.generated_by = generated_by
        self.week = week
        self.year = year
        self.date_generated = date_generated
        self.file_name = file_name
        self.comments = None


    def __repr__(self):
        return '<schedule for week {0} year {1} >'.format(self.week , self.year)



