from copy import deepcopy
import math
import itertools
from enum import Enum
import time

def snake_to_natural_case(string:str) -> str:
    try:
        # convert snakes to spaces
        unsnaked = string.replace('_', ' ')
        title_cased = ''
        for word in unsnaked.split(' '):
            title_cased += word[0].upper() + word[1:] + ' '
        return title_cased.strip()
    except: return string


class pocomp(Enum):
    EQUALS = 0
    GREATER_EQ = 1
    LESSER_EQ = 2


def po(pos_x: int, lam:float, po_comp:pocomp=pocomp.EQUALS):
    """
    Model the Poisson distribution. This can be used with significance levels to determine percentile.

    Get P(X=x) from X~Po(lambda). Use kwarg `po_comp`to change aggregation mode (=, ≤, ≥)"""


    if po_comp == pocomp.LESSER_EQ:
        # Sum all x lesser than and at x
        return sum (po(x, lam) for x in range(0,pos_x+1))
    if po_comp == pocomp.GREATER_EQ:
        # 1 - P(X≤x-1) will work P(X ≥ x)
        return 1 - po(pos_x-1, lam, pocomp.LESSER_EQ)

    return ( math.e**-lam * lam**pos_x ) / math.factorial(pos_x)


class sig_test_type(Enum):
    LOWER = 0
    UPPER = 1
    BOTH = 2


def past_significance_threshold(lam:int, test:int, significance:int, significance_2:int=None, testing=sig_test_type.LOWER):
    """
    Use the Poisson distribution to work out whether our test surpasses a significance level.
    """

    Po = lambda t: po(test, lam, t)

    if testing == sig_test_type.BOTH:
        lower = Po(pocomp.LESSER_EQ)
        upper = Po(pocomp.GREATER_EQ)
        if significance_2:
            return True if lower < significance or upper < significance_2 else False

        return True if lower < significance or upper < significance else False

    po_test = Po(pocomp.LESSER_EQ if testing == sig_test_type.LOWER else pocomp.GREATER_EQ)
    if po_test < significance: return True
    return False


def get_closest(l:list, v:float|int) -> float|int:
    # min returns smallest item in a provided list or arguments. Instead of providing the smallest,
    # configure the key kwarg so the one with the smallest absolute distance to our value is found.
    return min(l,key=lambda x:abs(x-v))

# print(past_significance_threshold(
#     lam=10,
#     test=11,
#     significance=5/100,
#     testing=sig_test_type.BOTH
# ))

def allperms(max_number, length):
    all_possible = []

    # all_combos = itertools.permutations(range(max_number+1), max_number+1)
    # print(list(all_combos))

    current_digits = [0 for _ in range(length)]

    
    def incr(ptr):
        if current_digits[ptr] == max_number:
            current_digits[ptr] = 0
            incr(ptr=ptr-1)
        else:
            current_digits[ptr] += 1

    while current_digits[0] < max_number:
        incr(-1)
        # print(current_digits)
        all_possible.append(deepcopy(current_digits))
    return all_possible


    # all_possible = []
    # selection_list = range(max_number+1)
    # digits = []
    # for i in range(length):
    #     digits.append(0)
    
    # for i in range(max_number**length):
    #     for d in range(length):
    #         r = len(digits)-1-d
    #         value = digits[r]
    #         value += 1
    #         digits[r] = value
    #         if value > max_number:
    #             value = 0
    #             digits[r] = value
    #             continue
    #         break

    
    # return [[0,0,0,0,0,0]]
        
    # print(all_possible)
    # return selection_list


class ClockResult:
    data:any
    stopwatch:int
    index: int

    def __init__(**kwargs):
        for kw in kwargs:
            setattr(kw, kwargs.get(kw))

def stopwatch(fn):
    def wrapper(*args, **kwargs) -> tuple[any, int]:
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        
        # return ClockResult(data=result, stopwatch=end-start)
        return (result, end-start)

    return wrapper


duplicates_dict:dict[dict[int]] = {}

def clear_old(id, old_threshold=10):
    target_dict = duplicates_dict.get(id)
    if not target_dict: return

    print (target_dict)

    for contents, t in deepcopy(target_dict).items():
        if time.time() - t > old_threshold:
            del target_dict[contents]

def getfile(file:str, default_ext='txt'):
    SEP = '.'
    default_ext = SEP + default_ext.replace(SEP,'')
    file = file.strip().replace(default_ext, '') + (default_ext if not SEP in file else '')
    try:
        with open(file, 'r') as f:
            return f.read()
        
    except FileNotFoundError:
        print(f'getfile(file={file}, default_ext={default_ext}): ERR cannot find file "{file}".')
        return False

def get_n_item(dictionary:dict, n:int):
    return list(dictionary.items())[n]

def similarity():
    return False
    # ! IMPLEMENT!
            
def prevent_duplicate_calls(id, fn, threshold=2, timeout_based=False, similarity_based=False, *args, **kwargs):
    clear_old(id, old_threshold=threshold)
    target_dict = duplicates_dict.get(id)

    if not target_dict:
        target_dict = {}
        duplicates_dict[id] = target_dict
    elif timeout_based and len(target_dict.keys()) > 0:
        return


    contents = str(args) + str(kwargs)

    if similarity_based:
        for key in target_dict:
            if similarity(key, contents) > 0.9:
                return
    else:
        if contents in target_dict: return
    
    # no duplicates detected. run and set contents

    target_dict[contents] = time.time()
    fn(*args, **kwargs)

def build_matrix(r:int, c:int, filler:str|int=0):
    return [[filler for col in range(c)] for row in range(r)]


class MatrixRowIterator:
    def __init__(self, matrix:list[list]):
        self.matrix = matrix
        self.row_ptr = 0
        self.col_ptr = 0
        self.row_max = len(matrix) - 1
        self.col_max = len(matrix[0]) - 1
        self.last = False

    def iter(self):
        return self.__iter__()
    

    def __iter__(self):
        return self
    def __next__(self):

        last_r = self.row_ptr
        last_c = self.col_ptr
        if self.row_ptr < self.row_max:
            self.row_ptr += 1
        elif self.col_ptr < self.col_max:
            self.row_ptr = 0
            self.col_ptr += 1
        else:
            if not self.last:
                self.last = True
            else:
                raise StopIteration
        
        return (last_r, last_c)


def print_matrix(matrix:list[list], highlight_targets:list[tuple[int,int]]=[]):
    current_col = 0
    out = ''
    for r,c in MatrixRowIterator(matrix=matrix).iter():
        if c != current_col:
            current_col = c
            out += '\n'
        if (r,c) in highlight_targets:
            out += f' ▶{matrix[r][c]}◀ '
        else:
            out += f'  {matrix[r][c]}  '

    print(out)


def get_matrix_loc(matrix: list[list], search:any, aliases:dict={}) -> tuple[int,int] | bool:
    for r,c in MatrixRowIterator(matrix=matrix).iter():
        result = matrix[r][c]
        if result == search or aliases.get(search) == result:
            return (r,c)
    print(f'ERR no finds for \'{search}\' in matrix:\n{print_matrix(matrix)}')
    return False




def matrix_get(m):
    def get( r_c: tuple[int,int] ):
        return m[r_c[0]][r_c[1]]
    return get



def decsv(csv_str: str) -> list[str]:
    return [item.strip() for item in csv_str.replace('\n','').split(',')]

def digraph(string:str, padding='X', step=2) -> list[str]:
    digraphs = []
    for i in range(0, len(string), step):
        if i+1 > len(string) -1:
            digraphs.append(string[i] + padding)
        digraphs.append(string[i:i+step])
    return digraphs
