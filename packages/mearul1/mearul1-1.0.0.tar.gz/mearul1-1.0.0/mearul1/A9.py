#Types of Methods
class Student:
    school_name = "XYZ International School"
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def show_details(self):
        return f"Name: {self.name}, Age: {self.age}"
    @classmethod
    def get_school_name(cls):
        return f"School: {cls.school_name}"
    @staticmethod
    def is_adult(age):
        return age >= 18

s1 = Student("ABC", 20)
print(s1.show_details())
print(Student.get_school_name())
print(Student.is_adult(17))


#Single Inheritance
class Person:
    def __init__(self, name):
        self.name = name
    def show(self):
        return f"Person: {self.name}"

class Student(Person):
    def __init__(self, name, course):
        super().__init__(name)
        self.course = course
    def show(self):
        return f"Student: {self.name}, Course: {self.course}"

s = Student("John", "Biotechnology")
print("\nSingle Inheritance:", s.show())


#Multilevel Inheritance
class Animal:
    def speak(self):
        return "Animal sound"

class Mammal(Animal):
    def speak(self):
        return "Mammal sound"

class Cat(Mammal):
    def speak(self):
        return "Cat meows"

m = Cat()
print("\nMultilevel Inheritance:", m.speak())


#Multiple Inheritance
class Father:
    def skill(self):
        return "Painting"

class Mother:
    def skill(self):
        return "Singing"

class Child(Father, Mother):
    def skill(self):
        return f"{Father.skill(self)}, {Mother.skill(self)}"

c = Child()
print("\nMultiple Inheritance:", c.skill())


#Hierarchical Inheritance
class Vehicle:
    def type(self):
        return "Vehicle"

class Car(Vehicle):
    def type(self):
        return "Sedan Car"

class Bike(Vehicle):
    def type(self):
        return "Sports Bike"

print("\nHierarchical Inheritance:")
print(Car().type())
print(Bike().type())


#Hybrid Inheritance
class A:
    def show(self):
        return "Class A"

class B(A):
    def show(self):
        return "Class B"

class C(A):
    def show(self):
        return "Class C"

class D(B, C):
    def show(self):
        return "Class D"

print("\nHybrid Inheritance:", D().show())


#Method Overriding
class Animal:
    def speak(self):
        return "Generic Animal sound"

class Dog(Animal):
    def speak(self):
        return "Dog barks"

class Parrot(Animal):
    def speak(self):
        return "Parrot talks"

print("\nMethod Overriding:")
for a in [Animal(), Dog(), Parrot()]:
    print(a.speak())


#Method Overloading
class MathOperation:
    def add(self, *args):
        return sum(args)

math = MathOperation()
print("\nMethod Overloading:")
print("Add 2 numbers:", math.add(3, 7))
print("Add 3 numbers:", math.add(2, 5, 8))
print("Add many numbers:", math.add(1, 2, 3, 4, 5))
