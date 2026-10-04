if __name__ != "__main__":
    from .cells import *
    from .env import *
    from .reproduction import *

class Sugar:
    def __init__(self, type, name=None):
        self.name = name
        self.type = type

class Pyruvic_acid:
	'''丙酮酸'''
	def __init__(self, amount=1,name=None):
		self.name = name
		self.amount = amount

class NADH:
	'''NADH'''
	def __init__(self, amount=1,name=None):
		self.name = name
		self.amount = amount

class Glucose():
	def __init__(self, amount=1,name=None):
		self.name = name
		self.amount = amount
	def glycolysis(self):
		'''糖酵解'''
		relist = [
			Pyruvic_acid(amount=self.amount*2),
			NADH(amount=self.amount*2),
			env.H2O(amount=self.amount*2),
		]
		return relist
	def 