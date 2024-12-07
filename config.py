# -*- coding: utf-8 -*-
import os
from flask_session import Session
from redis import Redis


class Config:
    # session stuff
    SESSION_PERMANENT = False
    # SESSION_SERVER_SIDE = True
    SESSION_TYPE = "redis"
    SESSION_REDIS = Redis(host="localhost", port=6379, db=0)

    # misc
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test_secret_key_22734123'
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 512 * 1024 * 1024
    ALLOWED_EXTENTIONS = ["py"]
    SESSION_TYPE = "filesystem"
