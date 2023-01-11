from re import S
from . import db,config
from flask_login import UserMixin
import sys
import jwt
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
from .helper_functions import test_and_set


# Crowd:
# 0 - all
# 1 - Only crowd sourced
# 2 - Only manual added

companies_tags = db.Table('companies_tags',
        #  db.Column('id', db.Integer, primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey(
        'companies.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey(
        'tags.id'), primary_key=True),
    db.PrimaryKeyConstraint('company_id', 'tag_id')
    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))

    @staticmethod
    def create(password):
        if len(User.query.all()) == 0:
            new = User(password = generate_password_hash(password,method='sha256'))
            db.session.add(new)
            db.session.commit()
            return new

    def update(self,password):
        self.password = generate_password_hash(password,method='sha256')
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def gen_token(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
            'iat': datetime.datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            config['creds']['secret'],
            algorithm='HS256'
        )

    def authenticate(self, password):
        return check_password_hash(self.password, password)




class Company(db.Model):
    __tablename__ = "companies"
    """
    Reps a company
    """
    id = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime)
    active = db.Column(db.Boolean)
    charmtalk = db.Column(db.Boolean)
    name = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    unique_selling_point = db.Column(db.String(1000))
    summer_job_description = db.Column(db.String(1000))
    summer_job_link = db.Column(db.String(1000))
    summer_job_deadline = db.Column(db.Date)
    contacts = db.Column(db.String(100))
    contact_email = db.Column(db.String(320))
    employees_world = db.Column(db.Integer)
    employees_sweden = db.Column(db.Integer)
    website = db.Column(db.String(200))
    talk_to_us_about = db.Column(db.String(1000))
    logo = db.Column(db.String(100))
    map_image = db.Column(db.Integer)
    booth_number = db.Column(db.Integer)
    tags = db.relationship(
        'Tag',
        secondary=companies_tags,
        lazy='subquery',
        backref=db.backref('tags', lazy=True, cascade='all, delete')
    )

    @staticmethod
    def create( name, active, charmtalk, description, unique_selling_point, summer_job_description,
               summer_job_link, summer_job_deadline, contacts, contact_email, employees_world,
               employees_sweden, website, talk_to_us_about, logo, map_image, booth_number, tags):
        try:
            if Company.query.filter_by(name=name).first():
                return False
            new_company = Company(
                name=name,
                last_updated=datetime.datetime.now(),
                active=active,
                charmtalk=charmtalk,
                description=description,
                unique_selling_point = unique_selling_point,
                summer_job_description = summer_job_description,
                summer_job_link = summer_job_link,
                summer_job_deadline = summer_job_deadline,
                contacts = contacts,
                contact_email = contact_email,
                employees_world = employees_world,
                employees_sweden = employees_sweden,
                website = website,
                talk_to_us_about = talk_to_us_about,
                logo = logo,
                map_image = map_image,
                booth_number = booth_number,
                tags = tags
            )

            db.session.add(new_company)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def update(self, name, active, charmtalk, description, unique_selling_point,
               summer_job_description, summer_job_link, summer_job_deadline, contacts,
               contact_email, employees_world, employees_sweden, website,
            talk_to_us_about,logo, map_image, booth_number, tags):

        self.name = test_and_set(self.name,name)
        self.last_updated = datetime.datetime.now()
        self.active = test_and_set(self.active,active)
        self.charmtalk = test_and_set(self.charmtalk,charmtalk)
        self.description = test_and_set(self.description,description)
        self.unique_selling_point = test_and_set(self.unique_selling_point, unique_selling_point)
        self.summer_job_description = test_and_set(self.summer_job_description, summer_job_description)
        self.summer_job_link = test_and_set(self.summer_job_link, summer_job_link)
        self.contacts = test_and_set(self.contacts,contacts)
        self.contact_email = test_and_set(self.contact_email,contact_email)
        self.employees_world = test_and_set(self.employees_world, employees_world)
        self.employees_sweden = test_and_set(self.employees_sweden, employees_sweden)
        self.website = test_and_set(self.website, website)
        self.logo = test_and_set(self.logo, logo)
        self.map_image = test_and_set(self.map_image, map_image)
        self.booth_number = test_and_set(self.booth_number, booth_number)
        self.talk_to_us_about = test_and_set(self.talk_to_us_about, talk_to_us_about)
        self.tags = test_and_set(self.tags, tags)

        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        tags = []
        for tag in self.tags:
            tags.append(tag.id)
        return {
            'id': self.id,
            'name': self.name,
            'last_updated': (self.last_updated + datetime.timedelta(hours=1, seconds=0)).strftime("%Y-%m-%mT%H:%M:%S"),
            'active': self.active,
            'charmtalk': self.charmtalk,
            'description': self.description,
            'unique_selling_point': self.unique_selling_point,
            'summer_job_description': self.summer_job_description,
            'summer_job_link': self.summer_job_link,
            'summer_job_deadline': self.summer_job_deadline,
            'contacts': self.contacts,
            'contact_email': self.contact_email,
            'employees_world': self.employees_world,
            'employees_sweden': self.employees_sweden,
            'website': self.website,
            'logo': self.logo,
            'map_image': self.map_image,
            'booth_number': self.booth_number,
            'talk_to_us_about': self.talk_to_us_about,
            'tags': tags
        }


class Tag(db.Model):
    __tablename__ = "tags"
    """
    Tag represents a buzzword, program, or talent.
    These can be crowd sourced.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    parent_tag = db.Column(db.Integer)
    up_votes = db.Column(db.Integer)
    down_votes = db.Column(db.Integer)
    crowd_sourced = db.Column(db.Boolean)
    icon = db.Column(db.String(100))
    division = db.Column(db.Boolean)
    business_area = db.Column(db.Boolean)
    looking_for = db.Column(db.Boolean)
    offering = db.Column(db.Boolean)
    language = db.Column(db.Boolean)
    fair_area = db.Column(db.Boolean)

    @staticmethod
    def create(name, parent_tag,up_votes, down_votes, crowd_sourced, icon, division, business_area, looking_for, offering, language, fair_area):
        try:
            if Tag.query.filter_by(name=name).first():
                return False
            new_tag = Tag(
                name=name,
                parent_tag=parent_tag,
                up_votes = up_votes,
                down_votes = down_votes,
                crowd_sourced=crowd_sourced,
                icon = icon,
                division = division,
                business_area = business_area,
                looking_for = looking_for,
                offering = offering,
                language = language,
                fair_area = fair_area,
            )
            db.session.add(new_tag)
            db.session.commit()
        except:
            return False
        return True

    def update(self,name, parent_tag,up_votes, down_votes, crowd_sourced, icon, division, business_area, looking_for, offering, language, fair_area):
        try:
            self.name = test_and_set(self.name,name)
            self.parent_tag = test_and_set(self.parent_tag,parent_tag)
            self.up_votes = test_and_set(self.up_votes,up_votes)
            self.down_votes = test_and_set(self.down_votes, down_votes)
            self.crowd_sourced = test_and_set(self.crowd_sourced,crowd_sourced)
            self.icon = test_and_set(self.icon, icon)
            self.division = test_and_set(self.division, division)
            self.business_area = test_and_set(self.business_area, business_area)
            self.looking_for = test_and_set(self.looking_for, looking_for)
            self.offering = test_and_set(self.offering, offering)
            self.language = test_and_set(self.language, language)
            self.fair_area = test_and_set(self.fair_area, fair_area)
            db.session.commit()
            return True
        except:
            return False


    def delete(self):
        db.session.delete(self)
        db.session.commit()

        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_tag': self.parent_tag,
            'up_votes': self.up_votes,
            'down_votes': self.down_votes,
            'crowd_sourced': self.crowd_sourced,
            'icon': self.icon,
            'division': self.division,
            'business_area': self.business_area,
            'looking_for': self.looking_for,
            'offering': self.offering,
            'language': self.language,
            'fair_area': self.fair_area
        }

class Tag_company(db.Model):
    """
    These are the reletion between a company and tag.
    These can be crowd source, it supports voting to improve the accuracy of the relation.
    """
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Integer)
    company = db.Column(db.Integer)
    votes = db.Column(db.Integer)
    score = db.Column(db.Integer)
    crowd_sourced = db.Column(db.Boolean)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'company': self.company,
            'up_votes': self.up_votes,
            'down_votes': self.down_votes,
            'crowd_sourced': self.crowd_sourced,
        }

    @staticmethod
    def create(tag, company, up_votes, down_votes, crowd_sourced):
        try:
            if Tag_company.query.filter_by(tag=tag,company=company).first():
                return False
            new_tag_company = Tag_company(
                tag=tag,
                company=company,
                up_votes=up_votes,
                down_votes=down_votes,
                crowd_sourced=crowd_sourced
            )

            db.session.add(new_tag_company)
            db.session.commit()
        except:
            return False
        return True

    def update(self, tag, company, up_votes, down_votes, crowd_sourced):
        try:
            self.tag = test_and_set(self.tag, tag)
            self.company = test_and_set(self.company,company)
            self.up_votes= test_and_set(self.up_votes, up_votes)
            self.down_votes= test_and_set(self.down_votes, down_votes)
            self.crowd_sourced = test_and_set(self.crowd_sourced, crowd_sourced)
            db.session.commit()
            return True
        except:
            return False

class Map(db.Model):
    __tablename__ = "maps"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(100))
    ref = db.Column(db.Integer)

    @staticmethod
    def create(name, image, ref):
        try:

            if Map.query.filter_by(name=name).first():
                return False
            new_map = Map(
                name = name,
                image = image,
                ref = ref
            )

            db.session.add(new_map)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def update(self, name, image, ref):
        self.name = test_and_set(self.name,name)
        self.image = test_and_set(self.image, image)
        self.ref = test_and_set(self.ref, ref)
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'ref': self.ref
        }

class Prepage(db.Model):
    __tablename__ = "prepages"
    """
    Reps a prepages
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(100))
    active = db.Column(db.Boolean)
    mobile = db.Column(db.Boolean)
    side = db.Column(db.String(5))
    page = db.Column(db.Integer)

    @staticmethod
    def create(name,active,image,mobile,side,page):

        try:
            if Prepage.query.filter_by(image=image).first():
                return False
            new_prepage = Prepage(
                name = name,
                image = image,
                active = active,
                mobile = mobile,
                side = side,
                page = page
            )

            db.session.add(new_prepage)
            db.session.commit()
        except Exception as e:
            print(e, file=sys.stderr)
            return False
        return True

    def update(self,name,active,image,mobile,side,page):
        self.name = test_and_set(self.name,name)
        self.active = test_and_set(self.active, active)
        self.image = test_and_set(self.image, image)
        self.mobile = test_and_set(self.mobile, mobile)
        self.side = test_and_set(self.side, side)
        self.page = test_and_set(self.page, page)
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'active': self.active,
            'mobile': self.mobile,
            'side': self.side,
            'page': self.page
        }

class Layout(db.Model):
    __tablename__ = "layout"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(100))
    active = db.Column(db.Boolean)
    placement = db.Column(db.Integer)

    @staticmethod
    def create(active,image, placement):
        try:
            if Layout.query.filter_by(image=image).first():
                return False
            new_layout = Layout(
                image = image,
                placement = placement,
                active = active
            )

            db.session.add(new_layout)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def update(self, active,image, placement):
        self.active = test_and_set(self.active, active)
        self.image = test_and_set(self.image, image)
        self.placement = test_and_set(self.placement, placement)
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'image': self.image,
            'placement': self.placement,
            'active': self.active
        }

class Shortcut(db.Model):
    __tablename__ = "shortcuts"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    desc = db.Column(db.String(100))
    link = db.Column(db.String(100))
    icon = db.Column(db.String(100))

    @staticmethod
    def create(name, desc, link, icon):
        try:
            new_shortcut = Shortcut(
                name=name,
                desc=desc,
                link=link,
                icon=icon
            )

            db.session.add(new_shortcut)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def update(self, name, desc, link, icon):
        self.name = test_and_set(self.name, name)
        self.desc = test_and_set(self.desc, desc)
        self.link = test_and_set(self.link, link)
        self.icon = test_and_set(self.icon, icon)
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc,
            'link': self.link,
            'icon': self.icon
        }

class Company_card(db.Model):
    __tablename__ = "company_cards"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    text = db.Column(db.String(100))
    active = db.Column(db.Boolean)

    @staticmethod
    def create(name, text, active):
        try:
            new_company_card = Company_card(
                name=name,
                text=text,
                active=active
            )

            db.session.add(new_company_card)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def update(self, name, text, active):
        self.name = test_and_set(self.name, name)
        self.text = test_and_set(self.text, text)
        self.active = test_and_set(self.active, active)
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'text': self.text,
            'active': self.active,
        }

class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(50))
    text = db.Column(db.String(1000))
    meta = db.Column(db.String(1000))
    received = db.Column(db.DateTime)

    @staticmethod
    def create(title, text, meta=""):
        try:
            new_feedback = Feedback(
                title=title,
                text=text,
                meta=meta,
                received=datetime.datetime.now()
            )

            db.session.add(new_feedback)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def update(self, title, text, meta):
        self.title = test_and_set(self.title, title)
        self.text = test_and_set(self.text, text)
        self.meta = test_and_set(self.meta, meta)
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'meta': self.meta,
            'received': self.received
        }
