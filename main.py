
class mA(type):
    def __new__(cls, name, bases, namespace):
        print('mA - __new__')
        return super().__new__(cls, name, bases, namespace)

class A(metaclass=mA):
    pass

class mB(type):
    def __new__(cls, name, bases, namespace):
        print('mB - __new__')
        return super().__new__(cls, name, bases, namespace)

class B(metaclass=mB):
    pass

class C(A):
    pass