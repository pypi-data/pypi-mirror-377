from abc import ABC, abstractmethod

#Abstract Figure
class Figure(ABC):
    @abstractmethod
    def area(self): pass
    @abstractmethod
    def perimeter(self): pass

class Square(Figure):
    def __init__(self,w,h): self.w,self.h=w,h
    def area(self): return self.w*self.h
    def perimeter(self): return 2*(self.w+self.h)

class Round(Figure):
    def __init__(self,r): self.r=r
    def area(self): return 3.14*self.r*self.r
    def perimeter(self): return 2*3.14*self.r

sq = Square(8,4)
rd = Round(6)
print(sq.area(), sq.perimeter())
print(rd.area(), rd.perimeter())


#Interfaces
class CanFly(ABC):
    @abstractmethod
    def fly(self): pass

class CanSwim(ABC):
    @abstractmethod
    def swim(self): pass

class Eagle(CanFly):
    def fly(self): return "Eagle above clouds"

class Shark(CanSwim):
    def swim(self): return "Shark under ocean"

class Penguin(CanFly,CanSwim):
    def fly(self): return "Penguin can’t fly"
    def swim(self): return "Penguin dives"

e,s,p = Eagle(),Shark(),Penguin()
print(e.fly(), s.swim(), p.fly(), p.swim(), sep="\n")
