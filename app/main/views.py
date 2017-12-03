from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response , send_file
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm , GenerateScheduleForm
from .. import db
from ..models import Permission, Role, User, Post, Comment , GeneratedSchedule , Ward , Requirement
from ..decorators import admin_required, permission_required
from os.path import isfile , join , os
import json , datetime
from ..email import send_email , send_email_with_attachment
from ..gen_pdf import generate_pdf , gen_pdf_table , generate_sample_schedule


def get_date_range(year , week):
    partial_date = "{0}-W{1}".format(year , week)
    date_1 = datetime.datetime.strptime(partial_date + '-1', "%Y-W%W-%w").strftime('%d, %b %Y')
    date_2 = datetime.datetime.strptime(partial_date + '-0' , "%Y-W%W-%w").strftime('%d, %b %Y')

    return  date_1 + '-' + date_2





@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    all_generated = db.session.query(GeneratedSchedule) \
        .all()

    generated_list = []
    for item in  all_generated:
        _year = item.year
        _week = item.week
        _date_range = get_date_range(year=_year , week = _week)
        _date_generated = item.date_generated.strftime('%Y-%m-%d')
        row = ( item.id , _year , _week , _date_range , _date_generated)
        generated_list.append(row)






    return render_template('index.html' , generated = generated_list)





@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)



@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/viewpdf/<int:id>', methods=['GET', 'POST'])
@login_required
def viewpdf(id):
    generated = GeneratedSchedule.query.get_or_404(id)
    file_name = generated.file_name
    #input_path = os.path.join('data/' , file_name)
    if file_name:


        return send_file(file_name)

        #return response






@main.route('/download/<int:id>', methods=['GET', 'POST'])
@login_required
def download(id):
    generated = GeneratedSchedule.query.get_or_404(id)
    file_name = generated.file_name
    #input_path = os.path.join('data/' , file_name)
    if file_name :
        return send_file(file_name ,
                         mimetype='text/pdf' ,
                         attachment_filename=file_name ,
                         as_attachment=True)

@main.route('/getGenerated', methods=[ 'POST'])
@login_required
def getGeneratedById():
    _id = request.form['id']

    generated = GeneratedSchedule.query.get_or_404(_id)
    retval = []
    retval.append({'Id':generated.id , 'week': generated.week , 'year':generated.year , 'file_name': generated.file_name })

    return json.dumps(retval)


@main.route('/sendmail', methods=[ 'POST'])
@login_required
def send_schedule():

    _recipients = request.form['recipients']
    _message = request.form['message']
    _week = request.form['week']
    _year = request.form['year']
    _date_range = get_date_range(week=_week , year=_year)
    _file_name = request.form['file_name']

    subject = "Attached is Generated schedule for date range {} ".format(_date_range)
    send_email_with_attachment(_recipients , subject ,
               'mail/schedule' ,
               week=_week , year=_year , message = _message , date_range = _date_range)

    return redirect(url_for('main.index'))


@main.route('/faq' , methods=[ 'GET' ])
def faq():
    return render_template('faq.html')

@main.route('/generateschedule', methods=[ 'GET' , 'POST'])
@login_required

def generateschedule() :
    ward_req = []
    form =GenerateScheduleForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('create_schedule.html' , form=form  , ward_req = ward_req)
        else:
            _year=form.year.data
            _week=form.week.data
            _comments = form.comments.data
            file_name = 'week' + str(_week) + '.pdf'

            file_path = 'data/'+ file_name

            pdf_path = 'app/' + file_path

            data = generate_sample_schedule()
            gen_pdf_table(pdf_path , data = data)

            data_row = GeneratedSchedule.query.filter(GeneratedSchedule.year ==_year , GeneratedSchedule.week == _week).first()
            if  data_row:
                data_row.week = _week
                data_row.year = _year
                data_row.comment = _comments
                data_row.file_name = file_path
            else:


                data_row = GeneratedSchedule(generated_by ='admin' , week = _week , year = _year , file_name = file_path , comments = _comments )

            db.session.add(data_row)


            return redirect(url_for('main.index'))

    else:
        ward_list = []
        wards = Ward.query.order_by('name').all()

        for w in wards:
            reqs = w.requirements

            for r in reqs:
                rq_name = r.name
                skill = r.skill.skill
                how_many1 = r.min_num_staff_s0
                how_many2 = r.min_num_staff_s1
                how_many3 = r.min_num_staff_s2
                tup_w = (w.name , rq_name , skill , how_many1 , how_many2 , how_many3)
                ward_list.append(tup_w)


        return render_template('create_schedule.html' , form=form , ward_list = ward_list)



