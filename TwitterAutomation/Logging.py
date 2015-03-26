import logging, os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from datetime import timedelta
import threading
import time
    
class TimedLogging(threading.Thread):
    def __init__(self, directory, interval):
        super(TimedLogging, self).__init__()
        self.directory = directory
        self.interval = interval
        self.time = str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %Hh%Mm%Ss'))
        self.timesup = False
        # Makes folder if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def run(self):
        try:
            start = datetime.now()
            while True:
                stop = datetime.now()
                
                elapsed = stop - start
                
                if elapsed >= timedelta(days=self.interval):
                    self.timesup = True
                    self.time = str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %Hh%Mm%Ss'))
                    start = datetime.now()
                    
        except OSError:
            pass
        
    def create_timed_log(self, text):
        completeName = self.directory + "/" + self.time + ".txt"
        logFile = open(completeName, 'a')
        logFile.write(text + "\n")
        logFile.close()
        
    def reset_log(self):
        completeName = self.directory + "/" + self.time + ".txt"
        open(completeName, 'w').close()
            
        
                