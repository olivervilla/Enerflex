from random import randint
import time
from threading import Thread

from multiprocessing import Pool


def function():
    a = randint(0, 5)
    time.sleep(a)
    print('Hilo con '+str(a)+' s')


def f(x):
    return x*x


# h = Thread(target=function, name='Hilo 1')
# h.start()

# h = Thread(target=function, name='Hilo 2')
# h.start()

# h = Thread(target=function, name='Hilo 3')
# h.start()

if __name__ == '__main__':
    t0 = time.time()
    p = Pool(5)
    print(p.map(f, [1,2,3,4,5,6]))
    # a = list()
    # for x in range(1, 7):
    #     a.append(f(x))
    
    # a = [f(i) for i in range(1,7)]

    # print(a)

    print('En '+str(time.time()-t0))