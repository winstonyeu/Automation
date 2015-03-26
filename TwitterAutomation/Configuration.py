import configparser

class Configuration():
    def __init__(self, filename):
        config = configparser.ConfigParser()
        try:
            open(filename, 'r').close()
        except FileNotFoundError:
            print("File doesn't exist!")
            
        config.read(filename)
         
        try:
            self.ConsumerKey    = config['AUTHENTICATION']['CONSUMER_KEY']
            self.ConsumerSecret = config['AUTHENTICATION']['CONSUMER_SECRET']
            self.AccessKey      = config['AUTHENTICATION']['ACCESS_KEY']
            self.AccessSecret   = config['AUTHENTICATION']['ACCESS_SECRET']
        except KeyError:
            print("No authentication keys")
    
    