# -*- coding: utf-8 -*-
from app import app
from utils import FileUtils
from flask_session import Session


if __name__ == '__main__':
    Session(app)
    app.run(debug=True)
