from pyDbs.gpy import *
from pyDbs.base import _numtypes

class GpyDict:
	def __init__(self, symbols = None):
		""" Simple keyword database with gpy symbols. 
			Slightly different logic than SimpleDB, as it allows for key!=self.symbols[key].name"""
		self.symbols = noneInit(symbols, {})

	def __getitem__(self,item):
		return self.symbols[item]

	def __setitem__(self,item,value):
		""" Add gpy directly with itentifier item:str, or using item:tuple. """
		if isinstance(value, Gpy_):
			self.symbols[item] = value
		elif isinstance(item, str):
			self.symbols[item] = Gpy.c(value, name = item)
		else:
			self.symbols[item[0]] = Gpy.c(value, name = item[1])

	def __call__(self, item, attr = 'v'):
		return getattr(self[item], attr)

	def set(self, item, value, **kwargs):
		""" Akin to setitem, but passes **kwargs to the Gpy.c function. """
		self.symbols[item[0]] = Gpy.c(value, name = item[1], **kwargs)

	def __iter__(self):
		return iter(self.symbols.values())

	def __delitem__(self,item):
		del(self.symbols[item])

	def __len__(self):
		return len(self.symbols)


class SimpleDB:
	def __init__(self, name = None, symbols = None, alias = None):
		self.name = name
		self.symbols = noneInit(symbols, {})
		self.updateAlias(alias = alias)

	def updateAlias(self,alias=None):
		self.alias = self.alias.union(pd.MultiIndex.from_tuples(noneInit(alias,[]), names = ['from','to'])) if hasattr(self,'alias') else pd.MultiIndex.from_tuples(noneInit(alias,[]), names = ['from','to'])

	def __iter__(self):
		return iter(self.symbols.values())

	def __len__(self):
		return len(self.symbols)

	def __delitem__(self,item):
		del(self.symbols[item])

	def copy(self):
		obj = type(self).__new__(self.__class__,None)
		obj.__dict__.update(deepcopy(self.__dict__).items())
		return obj

	def getTypes(self,types=None):
		return {k:v for k,v in self.symbols.items() if v.type in noneInit(types, ['variable'])}

	def getDomains(self, setName, types = None):
		return {k:v for k,v in self.getTypes(types).items() if setName in v.domains}

	@property
	def aliasDict(self):
		return {k: self.alias.get_level_values(1)[self.alias.get_level_values(0) == k] for k in self.alias.get_level_values(0).unique()}

	@property
	def aliasDict0(self):
		return {key: self.aliasDict[key].insert(0,key) for key in self.aliasDict}

	def getAlias(self,x,index_=0):
		if x in self.alias.get_level_values(0):
			return self.aliasDict0[x][index_]
		elif x in self.alias.get_level_values(1):
			return self.aliasDict0[self.alias.get_level_values(0)[self.alias.get_level_values(1)==x][0]][index_]
		elif x in self.getTypes(['set']) and index_==0:
			return x
		else:
			raise TypeError(f"{x} is not aliased")

	def __getitem__(self,item):
		return self.symbols[item]

	def __setitem__(self,item,value):
		if isinstance(value, Gpy_):
			self.symbols[item] = value
		else:
			self.symbols[item] = Gpy.c(value, name = item)

	def __call__(self, item, attr = 'v'):
		return getattr(self[item], attr)

	def set(self, item, value, **kwargs):
		self[item] = Gpy.c(value, name = item, **kwargs)

	def aom(self, symbol, **kwargs):
		gpyInst = Gpy.c(symbol,**kwargs)
		self.aomGpy(gpyInst, **kwargs)

	def aomGpy(self, symbol, **kwargs):
		if symbol.name in self.symbols:
			self[symbol.name].mergeGpy(symbol, **kwargs)
		else:
			self[symbol.name] = symbol

	def mergeDbs(self, dbOther, **kwargs):
		[self.aomGpy(symbol, **kwargs) for symbol in dbOther.symbols.values()];

	def readSets(self, types = None):
		""" Read sets from database symbols """
		[self.aom(set_, symbol.index.get_level_values(set_).unique()) for symbol in self.getTypes(types).values() for set_ in symbol.domains];

	