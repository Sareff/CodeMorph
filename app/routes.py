# -*- coding: utf-8 -*-
import os
from app import app
from flask import request, redirect, url_for, render_template
from utils import FileUtils

os.makedirs(app.config.get("UPLOAD_FOLDER"), exist_ok=True)

@app.route("/")
def index():
    return redirect(url_for("upload_files"))

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return 'No files part in the request', 400

        files = request.files.getlist('files[]')

        if not files:
            return 'No files selected', 400

        for file in files:
            if file and FileUtils.allowed_file(file.filename, app.config.get("ALLOWED_EXTENTIONS")):
                filename = FileUtils.secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                return f'File {file.filename} is not allowed', 400

        return redirect(url_for('diagram'))

    return render_template('upload.html')

@app.route('/diagram')
def diagram():
    # Получаем список загруженных файлов
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in uploaded_files]

    # Здесь вызываем парсер и анализатор
    # Например:
    # classes_data = analyze_files(file_paths)

    # Для примера создадим фиктивные данные

    classes_data = {
    'classes': [
        {
            'name': 'Person',
            'attributes': ['+ name: String', '+ age: Integer'],
            'methods': ['+ getName(): String', '+ setName(name: String)']
        },
        {
            'name': 'Student',
            'attributes': ['+ studentID: Integer'],
            'methods': ['+ getStudentID(): Integer'],
        },
        # ... другие классы ...
    ],
    'relationships': [
        {'from': 'Student', 'to': 'Person', 'type': 'inheritance'},
        # ... другие отношения ...
    ]
}

    return render_template('diagram.html', classes_data=classes_data)

@app.errorhandler(413)
def too_large(e):
    return 'Файл слишком большой', 413

@app.errorhandler(400)
def bad_request(e):
    return 'Неправильный запрос', 400
