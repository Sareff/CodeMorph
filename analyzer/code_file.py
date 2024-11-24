class Person:
    """This is the Person class, representing a generic person."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name


class Student(Person):
    """The Student class, inheriting from Person."""

    def __init__(self, name: str, age: int, student_id: int):
        super().__init__(name, age)
        self.student_id = student_id

    def get_student_id(self) -> int:
        return self.student_id
