import uuid

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from xerparser.reader import Reader
from collections import defaultdict
from flask_restx import Resource, Api, fields, Namespace
from werkzeug.datastructures import FileStorage
import os
import datetime

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://hemam:hassan@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class WBS(db.Model):
    """ WBS Model for storing wbs related details """
    __tablename__ = "wbs"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80))
    name = db.Column(db.String(80))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    schedule = db.relationship('Schedule', backref='wbs')
    parent_id = db.Column(db.Integer, db.ForeignKey('wbs.id'))
    parent = db.relationship(lambda: WBS, remote_side=id, backref='subs')
    public_id = db.Column(db.String(100), unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean)


class XER(db.Model):
    """ Model Model for storing subcontractor related details """
    __tablename__ = "xerfile"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    public_id = db.Column(db.String(100), unique=True)
    extension = db.Column(db.String(20))
    created_on = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean)


class Schedule(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "schedule"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    public_id = db.Column(db.String(100), unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean)


class ScheduleDto:
    api = Namespace('schedule', description='schedule related operations')
    schedule = api.model('schedule', {
        'id': fields.String(description='Unique ID'),
        'title': fields.String(required=True, description='Section name'),
        'public_id': fields.String(description='user Identifier'),
        'is_active': fields.Boolean(descripition='Active or not active')
    })


class WBSDto:
    api = Namespace('wbs', description='wbs related operations')
    wbs = api.model('wbs', {
        'id': fields.String(description='Unique ID'),
        'code': fields.String(required=True, description='WBS ID Code'),
        'name': fields.String(required=True, description='WBS name'),
        'schedule_public_id': fields.String(required=True, description='project identifier'),
        'parent_public_id': fields.String(description='parent wbs if it is a subwbs'),
        'public_id': fields.String(description='user Identifier'),
        'is_active': fields.Boolean(descripition='Active or not active')
    })


class XERDto:
    api = Namespace('xer', description='handles model uploads')
    model = api.model('xer', {
        'name': fields.String(descripition='name of the resource'),
        'public_id': fields.String(description='user Identifier'),
        'extension': fields.String(description="file extension as loaded by users"),
        'is_active': fields.Boolean(descripition='Active or not active')
    })


class ProjectDto:
    api = Namespace('project', description='project related operations')
    project = api.model('project', {
        'id': fields.String(description='Unique ID'),
        'name': fields.String(required=True, description='project name'),
        'is_active': fields.Boolean(descripition='Active or not active')
    })


def save_new_schedule(data):
    schedule = None
    new_schedule = Schedule(
        public_id=str(uuid.uuid4()),
        title=data['title'],
        created_on=datetime.datetime.utcnow(),
        is_active=True
    )
    save_changes(new_schedule)
    created_schedule = Schedule.query.filter_by(public_id=new_schedule.public_id).first()
    response_object = {
        'public_id': new_schedule.public_id,
        'status': 'success',
        'message': 'Successfully created.',
        'id': created_schedule.id
    }
    return response_object, 201


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.remove()


def save_new_wbs(data):
    schedule = Schedule.query.filter_by(public_id=data['schedule_public_id']).first()
    wbs = None
    if schedule:
        wbs = WBS.query.filter_by(code=data['code'], schedule_id=schedule.id).first()
    print(wbs)
    new_wbs = None
    if not wbs:
        parent_id = None
        if 'parent_public_id' in data:
            if data['parent_public_id'] == '':
                parent_public_id = None
            else:
                parent = WBS.query.filter_by(public_id=data['parent_public_id']).first()
                parent_id = parent.id
        else:
            parent_id = None
        print("parent", parent_id)
        new_wbs = WBS(
            public_id=str(uuid.uuid4()),
            code=data['code'],
            name=data['name'],
            schedule_id=schedule.id,
            parent_id=parent_id,
            created_on=datetime.datetime.utcnow(),
            is_active=True
        )
        save_changes(new_wbs)
        response_object = {
            'public_id': new_wbs.public_id,
            'status': 'success',
            'message': 'Successfully created.'
        }
        return response_object, 201

    else:
        response_object = {
            'status': 'fail',
            'message': 'WBS already exists. Please Log in.',
        }
        return response_object, 409


MODEL_UPLOADS = os.path.join(os.path.abspath('.'), 'schedules')
apixer = XERDto.api
_model = XERDto.model
upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)
upload_parser.add_argument('project_public_id')

@apixer.route('/')
class fileupload(Resource):
    apixer = XERDto.api
    schedule = apixer.parser()
    schedule.add_argument('file', location='files', type=FileStorage, required=True)

    @api.expect(schedule)
    def post(self):
        """ Upload Files """
        args = upload_parser.parse_args()
        public_id = str(uuid.uuid4())
        uploaded_file = args['file']  # This is FileStorage instance
        extension = uploaded_file.filename.split('.')[-1]
        uploaded_file.save(os.path.join(MODEL_UPLOADS, public_id + '.' + extension))
        new_model = XER(
            public_id=public_id,
            name=uploaded_file.filename,
            extension=extension,
            created_on=datetime.datetime.utcnow(),
            is_active=True)
        db.session.add(new_model)
        db.session.commit()
        source = os.path.join(MODEL_UPLOADS, public_id + '.' + extension)
        extract_data = Reader(source)
        args['xer_id'] = public_id
        self.extractdata(extract_data, args)
        return {'public_id': public_id}, 200

    def extractdata(self, extract_data, args):
        cnt = 0
        for p in extract_data.projects:
            print(p)
            data = {}
            data['title'] = p.proj_short_name
            data['project_public_id'] = args['project_public_id']
            s = save_new_schedule(data)
            s_p_id = s[0]['public_id']
            wbs_dic = {}
            for wbs in p.wbss:
                wbsdata = {}
                wbsdata['code'] = wbs.wbs_short_name
                wbsdata['name'] = wbs.wbs_name
                wbsdata['schedule_public_id'] = s_p_id
                wbsdata['parent'] = wbs_dic.get(wbs.parent_wbs_id)
                wbcur, stat = save_new_wbs(wbsdata)
                wbsdata['public_ic'] = wbcur.get('public_id')
                wbs_dic[wbs.wbs_id] = wbsdata
            print('progress', wbs_dic)

    def get(self):
        pass

api.add_namespace(XERDto.api)
# api.add_resource(fileupload, '/importxer')

app.run(host='0.0.0.0', port=5000, debug=True)
