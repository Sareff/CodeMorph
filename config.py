# -*- coding: utf-8 -*-
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test_secret_key_22734123'
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 512 * 1024 * 1024
    ALLOWED_EXTENTIONS = ["py"]
