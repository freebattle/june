import hashlib
from datetime import datetime
from random import choice
from flask import g
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(400))
    website = db.Column(db.String(400))

    role = db.Column(db.Integer, default=1)
    # 0: registered,  1: username
    reputation = db.Column(db.Integer, default=20, index=True)
    token = db.Column(db.String(16))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    city = db.Column(db.String(200))
    edit_username_count = db.Column(db.Integer, default=2)
    description = db.Column(db.Text)

    def __init__(self, email, **kwargs):
        self.email = email.lower()
        self.token = self.create_token(16)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_avatar(self, size=48):
        if self.avatar:
            return self.avatar
        md5email = hashlib.md5(self.email).hexdigest()
        query = "%s?s=%s%s" % (md5email, size, g.gravatar_extra)
        return g.gravatar_base_url + query

    def to_json(self):
        data = (
            '{"username":"%s", "avatar":"%s", "website":"%s",'
            '"reputation":%s, "role":%s}'
        ) % (self.username, self.get_avatar(), self.website or "",
             self.reputation, self.role)
        return data

    @staticmethod
    def create_password(raw):
        salt = Member.create_token(8)
        hsh = hashlib.sha1(salt + raw + g.password_secret).hexdigest()
        return "%s$%s" % (salt, hsh)

    @staticmethod
    def create_token(length=16):
        chars = ('0123456789'
                 'abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        salt = ''.join([choice(chars) for i in range(length)])
        return salt

    def check_password(self, raw):
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        verify = hashlib.sha1(salt + raw + g.password_secret).hexdigest()
        return verify == hsh

    @property
    def is_staff(self):
        return self.role > 6

    @property
    def is_admin(self):
        return self.role > 9
