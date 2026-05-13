from collections.abc import Callable

class Queue:
    queue: list[Callable]
    id:str
    driving:bool
    driverCallable:Callable
    remainingRecurseCallable:Callable

    def __init__(self, queue:list[Callable]=[], id:str|None=None):
        self.queue = queue
        self.id = id
        self.driving = False
        self.driverCallable = lambda: None
        self.remainingRecurseCallable = lambda: None


    def get_id (self):
        return self.id


    def set_id(self, id:str):
        self.id = id


    def push (self, *callbacks:list[Callable]):
        for callback in callbacks:
            self.queue.append(callback)



    def setDriveCallable(self, callback:Callable):
        self.driverCallable = callback

    def setRemainingRecurseCallable(self, callback:Callable):
        self.remainingRecurseCallable = callback


        
    def drive (self, callback:Callable, _m_rec_depth=0):
        if not callback: callback = self.driverCallable
        self.driverCallable = callback

        if self.driving == True or len(self.queue) == 0:
            return
        self.driving = True
        
        startSize = len(self.queue)

        i = 0
        while i < len(self.queue):
            if (len(self.queue) > startSize):
                print('Queue has grown. From', startSize, 'to', len(self.queue))
        
            self.driverCallable(self.queue[i](), len(self.queue) - 1)
            self.queue.remove(i)

            i += 1
    
        self.driving = False
        if len(self.queue) > 0 and _m_rec_depth < 10:
            # info('RECURSING drive, there are '+len(self.queue)+' messages to recurse through')
            self.remainingRecurseCallable(len(self.queue))
            self.drive(self.driverCallable, _m_rec_depth+1)


class QueueCollection:
    queues: list[Queue]

    def __init__(self, queues:list[Queue]=[]):
        self.queues = queues


    def add (self, queue: Queue):
        self.queues.append(queue)
        return queue


    def find (self, id:str) -> Queue:
        # self.queues.
        for queue in self.queues:
            if queue.get_id() == id:
                return queue


    def find_else_add (self, id:str):
        find = self.find(id)
        return find if find else self.add(Queue([], id))


