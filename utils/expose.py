from utils.bindutils import *

def expose_args(holds:dict[Hold]):
    def deco(fn):
        def wrapper(*args, **kwargs):
            #if a kwargs is getexposed, we instead return the holds

            if kwargs.get('getexposed', False):
                return holds
            
            return fn(*args, **kwargs) # normal case: return result of function
        return wrapper # the wrapper will be executed instead
    return deco # The decorator is returned as part of a deco factory