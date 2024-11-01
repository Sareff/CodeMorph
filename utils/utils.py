# -*- coding: utf-8 -*-
from typing import List
import os
import re
import unicodedata

class FileUtils:
    def allowed_file(filename: str, extentions: List[str]) -> bool:
        """
        Проверяет имеет ли файл filename разрешенное расширение из списка extentions
        """
        return "." in filename and filename.rsplit(".", 1)[1].lower() in extentions

    def secure_filename(filename):
        """
        Преобразует имя файла в безопасный формат для использования на файловой системе.
        Удаляет опасные символы и предотвращает атаки типа "directory traversal".
        """
        if isinstance(filename, str):
            # Нормализация Unicode-символов
            filename = unicodedata.normalize('NFKD', filename)
            filename = filename.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        else:
            # Если это не строка, декодируем в строку
            filename = filename.decode('utf-8', 'ignore')

        # Заменяем разделители директорий на пробелы
        filename = filename.replace(os.path.sep, ' ')

        # Удаляем все нежелательные символы (оставляем буквы, цифры, точки, дефисы и подчеркивания)
        filename = re.sub(r'[^\w\.\- ]', '', filename)

        # Убираем начальные и конечные пробелы
        filename = filename.strip()

        # Заменяем последовательности пробелов на один подчеркивания
        filename = re.sub(r'\s+', '_', filename)

        # Ограничиваем длину имени файла (например, до 255 символов)
        max_length = 255
        filename = filename[:max_length]

        # Предотвращаем пустое имя файла
        if not filename:
            filename = 'unnamed'

        return filename
