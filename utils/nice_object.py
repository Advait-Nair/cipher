import inspect
from utils.generic import snake_to_natural_case


class NiceObject:
    """A NiceObject allows you to return output similar to a dictionary, but with a class-like attribution-getting syntax. This is achieved by allowing functions to return a Class with their dict keys and values in attribute form. In order to allow typing, simply extend the class and provide the class attribute key and type hint."""
    __renamed_mapping = {}
    def __init__(self, **kwargs):
        for kw in kwargs:
            self[kw] = kwargs.get(kw)
    def __setitem__(s,k,v): setattr(s,k,v)
    def __getitem__(s,k): getattr(s,k)
    def __delitem__(s,k): delattr(s,k)

    def rename(self, attr, new_name):
        # Swap names
        # self[new_name] = self[attr]
        self.__renamed_mapping[attr] = new_name

        # # Reference to old name
        # self.__renamed_mapping[new_name] = '__' + attr

        # # self.attr -> self.__atr
        # self['__' + attr] = self[attr]
        # del self[attr]

    def as_table(self, key_header='Key', value_header='Value') -> list[dict]:

        kv_list = []

        provided_attributes = inspect.getmembers(self, lambda a: not inspect.isroutine(a))
        for attr, value in provided_attributes:
            if '__' in attr: continue
            name = self.__renamed_mapping[attr] if self.__renamed_mapping.get(attr) else snake_to_natural_case(attr)
            # value = self[attr]
            kv_list.append(
                dict(zip([key_header, value_header],[name,value]))
            )
            
        return kv_list
