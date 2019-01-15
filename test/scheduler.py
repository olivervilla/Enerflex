import time
import schedule
from threading import Thread
from datetime import datetime as dt

class Testeo():
    def __init__(self, name):
        self.name = name
        Thread(name='Schudeler\'s Launcher', target=self.launch_scheduler).start()
    
    def task_to_do(self):
        print('Doing insertion in table *{}*'.format(self.name))
        time.sleep(5)
        print('Im finish :) at {}')

    def launch_scheduler(self):
        schedule.every(20).seconds.do(self.task_to_do)
        # schedule.every(5).minutes.do(self.task_to_do)

        while(True):
            schedule.run_pending()
            time.sleep(1)

    def main_loop(self):
        while True:
            print('Doing stuffs')
            time.sleep(25)
            print('Ending stuffs')
            time.sleep(15)
            print('Finish :)')
            print('-'*20)
        

if __name__ == '__main__':
    mTest = Testeo('Prueba')
    mTest.main_loop()
    