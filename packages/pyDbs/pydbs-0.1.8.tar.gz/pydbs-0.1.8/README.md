# pyDbs
The current repo contains the code for the pypi package ```pyDbs```. The package is used to add specific structure to data using popular python packages like pandas and numpy. 

The package contains three main files: 
1. base.py: This defines classes "adj", "Broadcast", "ExcelSymbolLoader", and "adjMultiIndex". 
2. gpy.py: This defines symbol classes "GpySet, GpyVariable", and "GpyScalar", to give structure to symbols added using pandas series, pandas indices, or scalars. 
3. simpleDB.py: This defines two simple database classes "GpyDict" and "SimpleDB". The GpyDict class is a simple keyword database with Gpy symbols with a few auxiliary methods included. The "SimpleDB" is also a simple keyword database with Gpy symbols, but with a bit more structure. For instance, it features "aliased sets" as in GAMS, add-or-merge methods, a mergeDbs that allows merging with another SimpleDB instance, and it can add all relevant GpySets to the database by reading from already defined variables (```readSets``` method).

