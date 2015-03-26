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
            self.AccessToken = config['AUTHENTICATION']['ACCESS_TOKEN']
            self.ClientID    = config['AUTHENTICATION']['CLIENT_ID']
        except KeyError:
            print("No authentication keys")
    
    