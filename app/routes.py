# -*- coding: utf-8 -*-
import os
from app import app
from flask import request, redirect, url_for, render_template, flash, session
from utils import FileUtils

app.secret_key = '123SUPERSECRET'


UPLOAD_FOLDER = app.config.get("UPLOAD_FOLDER")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return redirect(url_for("upload"))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'code_file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)
        file = request.files['code_file']
        if file.filename == '':
            flash('Файл не выбран')
            return redirect(request.url)
        if file and FileUtils.allowed_file(file.filename, app.config.get("ALLOWED_EXTENTIONS")):
            filename = FileUtils.secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Анализируем загруженный файл
            classes_data = FileUtils.analyze_code(file_path)
            print(classes_data)

            # Удаляем загруженный файл после анализа (по желанию)
            os.remove(file_path)

            # Передаём данные в шаблон для построения диаграммы
            session['classes_data'] = classes_data
            return redirect(url_for('diagram'))
        else:
            flash('Разрешены только файлы с расширением .py')
            return redirect(request.url)
    else:
        return render_template('upload.html')


@app.route('/diagram')
def diagram():
    classes_data = session.get('classes_data')
    if not classes_data:
        flash('Нет данных для отображения диаграммы.')
        return redirect(url_for('upload'))
    return render_template('diagram.html', classes_data=classes_data)


@app.route('/class/<class_name>')
def class_page(class_name):
    classes_data = session.get('classes_data')
    if not classes_data:
        flash('Нет данных о классах. Пожалуйста, загрузите файл с кодом.')
        return redirect(url_for('upload'))

    # Ищем информацию о классе
    class_info = None
    for cls in classes_data['classes']:
        if cls['name'] == class_name:
            class_info = cls
            break

    if class_info:
        return render_template('class.html', class_info=class_info)
    else:
        return f"Класс {class_name} не найден.", 404


@app.errorhandler(413)
def too_large(e):
    return 'Файл слишком большой', 413


@app.errorhandler(400)
def bad_request(e):
    return 'Неправильный запрос', 400
