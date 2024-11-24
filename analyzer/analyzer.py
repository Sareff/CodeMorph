import ast
import json


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.relationships = []
        self.current_class = None
        self.class_names = set()
        self.type_mapping = {
            'str': 'String',
            'int': 'Integer',
            'float': 'Float',
            'bool': 'Boolean',
            'list': 'List',
            'dict': 'Dictionary',
            'set': 'Set',
            'tuple': 'Tuple',
            'None': 'void',
            # Добавьте другие типы по необходимости
        }
        self.local_vars = None  # Для отслеживания локальных переменных в методах

    def visit_ClassDef(self, node):
        class_name = node.name
        self.class_names.add(class_name)

        class_info = {
            'name': class_name,
            'attributes': [],
            'methods': [],
            'info': ast.get_docstring(node) or ''
        }
        self.current_class = class_info

        # Обработка базовых классов для наследования
        for base in node.bases:
            base_name = self.get_base_name(base)
            if base_name:
                # Добавляем связь наследования
                self.relationships.append({'from': class_name, 'to': base_name, 'type': 'inheritance'})

        self.generic_visit(node)

        self.classes.append(class_info)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class is not None:
            self.local_vars = {}  # Инициализируем словарь локальных переменных
            method_name = node.name
            visibility = '+'

            # Получаем параметры метода с типами (если есть аннотации)
            params = []
            for arg in node.args.args[1:]:  # Пропускаем 'self'
                param_name = arg.arg
                if arg.annotation:
                    param_type = self.get_annotation(arg.annotation)
                    param = f"{param_type} {param_name}"
                    self.local_vars[param_name] = param_type  # Сохраняем тип параметра
                else:
                    param = param_name
                    self.local_vars[param_name] = ''  # Тип неизвестен
                params.append(param)

            params_str = ', '.join(params)

            # Получаем возвращаемый тип (если есть аннотация)
            return_type = ''
            if node.returns:
                return_type = self.get_annotation(node.returns)

            method_signature = f"{visibility}{method_name}({params_str}) {return_type}".strip()
            self.current_class['methods'].append(method_signature)

            # Обходим тело метода
            self.generic_visit(node)

            # Сбрасываем локальные переменные после выхода из метода
            self.local_vars = None
        else:
            self.generic_visit(node)

    def visit_Assign(self, node):
        if self.current_class is not None and self.local_vars is not None:
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name) and target.value.id == 'self':
                        attr_name = target.attr
                        visibility = '+'
                        attr_type = ''
                        # Пытаемся получить тип из правой части присваивания
                        if isinstance(node.value, ast.Name):
                            var_name = node.value.id
                            attr_type = self.local_vars.get(var_name, '')
                        elif isinstance(node.value, ast.Call):
                            attr_type = self.get_call_type(node.value)
                        elif isinstance(node.value, ast.Constant):
                            value_type = type(node.value.value).__name__
                            attr_type = self.type_mapping.get(value_type.lower(), value_type)
                        attr = f"{visibility}{attr_type} {attr_name}".strip()
                        # Избегаем дублирования атрибутов
                        if attr not in self.current_class['attributes']:
                            self.current_class['attributes'].append(attr)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        # Если вы хотите обрабатывать аннотированные присваивания (Python 3.6+)
        if self.current_class is not None:
            if isinstance(node.target, ast.Attribute):
                if isinstance(node.target.value, ast.Name) and node.target.value.id == 'self':
                    attr_name = node.target.attr
                    visibility = '+'
                    attr_type = self.get_annotation(node.annotation)
                    attr = f"{visibility}{attr_type} {attr_name}".strip()
                    if attr not in self.current_class['attributes']:
                        self.current_class['attributes'].append(attr)
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.current_class is not None:
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.class_names and func_name != self.current_class['name']:
                    # Добавляем ассоциацию
                    self.relationships.append(
                        {'from': self.current_class['name'], 'to': func_name, 'type': 'association'})
        self.generic_visit(node)

    def get_base_name(self, base):
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return self.get_full_name(base)
        else:
            return ''

    def get_full_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.get_full_name(node.value) + '.' + node.attr
        else:
            return ''

    def get_annotation(self, node):
        if isinstance(node, ast.Name):
            type_name = node.id
            return self.type_mapping.get(type_name, type_name)
        elif isinstance(node, ast.Subscript):
            value = self.get_annotation(node.value)
            slice = self.get_annotation(node.slice)
            return f"{value}[{slice}]"
        elif isinstance(node, ast.Attribute):
            return self.get_full_name(node)
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ''

    def get_call_type(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name[0].isupper():
                return func_name
            else:
                return self.type_mapping.get(func_name, func_name)
        return ''

    def get_return_annotation(self, node):
        if node.returns:
            return self.get_annotation(node.returns)
        else:
            return ''


if __name__ == '__main__':
    with open('test_code.py', 'r', encoding='utf-8') as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    classes_data = {
        'classes': analyzer.classes,
        'relationships': analyzer.relationships
    }

    with open('classes_data.json', 'w', encoding='utf-8') as f:
        json.dump(classes_data, f, ensure_ascii=False, indent=4)
