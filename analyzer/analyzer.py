import ast
import json


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.current_class = None

    def visit_ClassDef(self, node):
        class_info = {
            'name': node.name,
            'bases': [self.get_base_name(base) for base in node.bases],
            'methods': [],
            'attributes': [],
            'associations': set(),
        }
        self.current_class = class_info

        self.generic_visit(node)

        # Преобразуем set в список
        class_info['associations'] = list(class_info['associations'])

        self.classes.append(class_info)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class is not None:
            method_info = {
                'name': node.name,
                'args': [arg.arg for arg in node.args.args if arg.arg not in ('self', 'cls')],
                'returns': self.get_return_annotation(node),
            }
            self.current_class['methods'].append(method_info)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if self.current_class is not None:
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name) and target.value.id == 'self':
                        attr_name = target.attr
                        self.current_class['attributes'].append(attr_name)
                elif isinstance(target, ast.Name):
                    attr_name = target.id
                    self.current_class['attributes'].append(attr_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.current_class is not None:
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name[0].isupper():
                    self.current_class['associations'].add(func_name)
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

    def get_return_annotation(self, node):
        if node.returns:
            return ast.unparse(node.returns)
        else:
            return None


if __name__ == '__main__':
    source_code = r'''
class Person:
    """lol"""
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
'''

    tree = ast.parse(source_code)
    print(ast.dump(tree, indent=2))
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    # Сохраняем данные в JSON
    classes_data = {
        'classes': analyzer.classes
    }

    with open('classes_data.json', 'w', encoding='utf-8') as f:
        json.dump(classes_data, f, ensure_ascii=False, indent=4)
