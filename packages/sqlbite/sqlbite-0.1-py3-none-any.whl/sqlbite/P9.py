class Student:
    school_name = "ABC Public School"
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def show_details(self):
        return f"Name: {self.name}, Age: {self.age}"
    @classmethod
    def get_school_name(cls):
        return f"School Name: {cls.school_name}"
    @staticmethod
    def is_adult(age):
        return age >= 18

print("\nTypes of Methods")
s1 = Student("Nirbhay", 22)
print(s1.show_details())
print(Student.get_school_name())
print(Student.is_adult(20))

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

class Animal:
    def speak(self):
        return "Animal makes a sound"

class Mammal(Animal):
    def speak(self):
        return "Mammal makes some sound"

class Dog(Mammal):
    def speak(self):
        return "Dog barks"

class Father:
    def skill(self):
        return "Gardening"

class Mother:
    def skill(self):
        return "Cooking"

class Child(Father, Mother):
    def skill(self):
        return f"Father's skill: {Father.skill(self)}, Mother's skill: {Mother.skill(self)}"

class Vehicle:
    def type(self):
        return "This is a vehicle"

class Car(Vehicle):
    def type(self):
        return "This is a car"

class Bike(Vehicle):
    def type(self):
        return "This is a bike"

class A:
    def show(self):
        return "Class A"

class B(A):
    def show(self):
        return "Class B (from A)"

class C(A):
    def show(self):
        return "Class C (from A)"

class D(B, C):
    def show(self):
        return "Class D (from B and C)"

print("\nSingle Inheritance")
s = Student("Ravi", "Computer Science")
print(s.show())

print("\nMultilevel Inheritance")
d = Dog()
print(d.speak())

print("\nMultiple Inheritance")
c = Child()
print(c.skill())

print("\nHierarchical Inheritance")
car = Car()
bike = Bike()
print(car.type())
print(bike.type())

print("\nHybrid Inheritance")
d_obj = D()
print(d_obj.show())

class Animal:
    def speak(self):
        return "Animal makes a sound"

class Dog(Animal):
    def speak(self):
        return "Dog barks"

class Cat(Animal):
    def speak(self):
        return "Cat meows"

class MathOperation:
    def add(self, *args):
        result = 0
        for num in args:
            result = result + num
        return result

print("\nMethod Overriding")
animals = [Animal(), Dog(), Cat()]
for a in animals:
    print(a.speak())

print("\nMethod Overloading")
math = MathOperation()
print("Add two numbers", math.add(5, 10))
print("Add three numbers", math.add(5, 10, 15))
print("Add multiple numbers", math.add(1, 2, 3, 4, 5))
