class Hold:
    def __init__(self, v=0, subproperties:dict={}):
        self.value = v
        self.subproperties = subproperties
        self.setfn = lambda: None
    
    def getsp(self, sp_id):
        return self.subproperties.get(sp_id, False)
    def sp_exists(self, sp_id):
        not_defined_identifier = '__not_exists_in_dict__'
        result = self.subproperties.get(sp_id, not_defined_identifier)
        return True if result != not_defined_identifier else False

    def bind_fn(self, fn):
        self.setfn = fn
    
    def __set__(self, inst, nv):
        self.setfn()


    def t(self):
        return 'value'
    def set(self, v):
        self.value = v
    def incr(self, n):
        if type(self.value) in [int, float]:
            self.value += n
    def decr(self, n): self.incr(-n if type(self.value) in [int, float] else 0)



    def type(self): return type(self.value)