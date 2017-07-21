import sys
import config

from functools import reduce

def union_dict(*objs,f = lambda x,y: x + y, initial = 0):
	"""
	合并多个字典，相同的键，值相加
	
	union_dict({'a':1, 'b':2, 'c':3}, {'a':2, 'b':3}) ----> {'a':3, 'b':5, 'c':3}
	
	Arguments:
		*objs {dict} -- 要合并的字典
	
	Returns:
		[dict] -- 合并后的字典
	"""
	keys = set(sum([list(obj.keys()) for obj in objs],[]))
	total = {}  
	for key in keys:
		total[key] = reduce(f,[obj.get(key,initial) for obj in objs])
	return total 
	
def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0  
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
