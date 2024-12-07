# -*- coding: utf-8 -*-
import os
from app import app
from flask import request, redirect, url_for, render_template, flash, session
from utils import FileUtils

UPLOAD_FOLDER = app.config.get("UPLOAD_FOLDER")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return redirect(url_for("upload"))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Проверяем, были ли отправлены файлы
        if 'code_files' not in request.files:
            flash('Файлы не выбраны')
            return redirect(request.url)

        files = request.files.getlist('code_files')
        if not files or files[0].filename == '':
            flash('Файлы не выбраны')
            return redirect(request.url)

        saved_files = []
        for file in files:
            if file and FileUtils.allowed_file(file.filename, extentions=app.config.get("ALLOWED_EXTENTIONS")):
                filename = FileUtils.secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                saved_files.append(file_path)
            else:
                flash(f'Файл {file.filename} имеет недопустимое расширение и будет пропущен.')

        if not saved_files:
            flash('Нет допустимых файлов для анализа.')
            return redirect(request.url)

        # Анализируем загруженные файлы
        classes_data = FileUtils.analyze_files(saved_files)
        print(classes_data)

        # Удаляем загруженные файлы после анализа
        for file_path in saved_files:
            os.remove(file_path)

        # Сохраняем данные в сессии
        session['classes_data'] = classes_data

        # Перенаправляем на диаграмму
        return redirect(url_for('diagram'))
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
