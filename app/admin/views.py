from flask import render_template, redirect, request, url_for, flash
import flask_login as login
from ..admin_blueprint import AdminBlueprint

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, form

from flask_admin import Admin, BaseView, expose
from ..models import  User , Nurse , \
    NurseSkills, Skill , Ward , Requirement , NurseVacations , GeneratedSchedule , db
from wtforms import HiddenField

class MyModelView(ModelView):

    can_export = True






app = AdminBlueprint('admin2', __name__,url_prefix='/admin2',static_folder='static', static_url_path='/static/admin')

models = [Nurse ,NurseSkills, Skill, Ward, Requirement, NurseVacations,  GeneratedSchedule , User ]
for model in models:
    app.add_view(
        MyModelView(model, db.session,
                        category='Models')
    )



