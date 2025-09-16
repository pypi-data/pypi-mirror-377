from abc import ABC, abstractmethod

class Figure(ABC):
    @abstractmethod
    def area(self):
        pass
    @abstractmethod
    def perimeter(self):
        pass

class Square(Figure):
    def __init__(self, side1, side2):
        self.side1 = side1
        self.side2 = side2
    def area(self):
        return self.side1 * self.side2
    def perimeter(self):
        return 2 * (self.side1 + self.side2)

class Round(Figure):
    def __init__(self, r):
        self.r = r
    def area(self):
        return 3.14 * self.r * self.r
    def perimeter(self):
        return 2 * 3.14 * self.r

sq = Square(8, 4)
rd = Round(6)
print(sq.area(), sq.perimeter())
print(rd.area(), rd.perimeter())

class CanFly(ABC):
    @abstractmethod
    def fly(self):
        pass

class CanSwim(ABC):
    @abstractmethod
    def swim(self):
        pass

class Eagle(CanFly):
    def fly(self):
        return "Eagle above the clouds"

class Shark(CanSwim):
    def swim(self):
        return "Shark under the ocean waves"

class Penguin(CanFly, CanSwim):
    def fly(self):
        return "Penguin can’t truly fly"
    def swim(self):
        return "Penguin dives into the sea"

e = Eagle()
s = Shark()
p = Penguin()
print(e.fly())
print(s.swim())
print(p.fly())
print(p.swim())
