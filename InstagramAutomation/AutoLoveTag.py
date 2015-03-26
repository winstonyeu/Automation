# -*- coding: utf-8 -*-
from instagram.client import InstagramAPI
import urllib.request as urllib2
import json, codecs, time
from random import randint
from instagram.bind import InstagramAPIError
import Configuration
import Logging

config = Configuration.Configuration('config.ini')
access_token = config.AccessToken
client_id    = config.ClientID
api = InstagramAPI(access_token=access_token)

# A class for user info
class UserInfo:
    def __init__(self, username, mediaid, mediatext):
        self.Username = username
        self.MediaID = mediaid
        self.MediaText = mediatext

# A class that manages keywords from a file (keywords.txt)
# Can add more words into the file    
class Keywords:
    filename = open('keywords.txt', 'r')
    words = filename.read().splitlines()
    filename.close()
    
    keywordsDict = {}
    
    for word in words:
        keywordsDict[word] = 0
        
    # Returns respective word from text file when index is specified (0 = diary memories, 1 = video diary etc.)
    def IDToWords (self, num, precise):
        if precise:
            return '"' + self.words[num] + '"'
        else:
            return self.words[num]
    
    # Returns number to words in text file in array terms (Length - 1)
    def WordsLength (self):
        return len(self.words) - 1
    
    # Generates random index from the number of words
    def RandomWords (self, num = -1):
        if num == -1:
            listNum = randint(0, Keywords().WordsLength())
        else:
            listNum = num
        print("Keyword: " + self.words[listNum])
        return self.words[listNum]
    
    def AddKeywordsToDict(self, word, num):
        for key, value in self.keywordsDict.items():
            if key == word:
                self.keywordsDict[key] = value + num
                
    def ResetKeywordsDict(self):
        for word in self.words:
            self.keywordsDict[word] = 0
            
# A class to automate loving user's post with post that has specified keywords/hashtags                  
class AutoLove:
    TAGURL = 'https://api.instagram.com/v1/media/%s?access_token=%s'
    USERNAMEFILE = "likedHashTagUser.txt"
    ENDBUFFERTIME = 15 * 60
    
    keywords = Keywords()
    TagLog = Logging.TimedLogging("TLog", 1)
    TagLog.start()
    
    # Writes liked user name into a file (likedUser.txt)
    def WriteNameToFile(self, username):
        userFile = open(self.USERNAMEFILE, 'a')
        userFile.write(username)
        userFile.write('\n')
        userFile.close()
     
    # Convert URL to JSON data   
    def DecodeJSONData(self, url):
        response = urllib2.urlopen(url)
        reader = codecs.getreader("utf-8")
        decodedData = json.load(reader(response)) 
        return decodedData
    
    # Gets media ID from a single line (e.g. Media: 918328349) 
    def GetMediaID(self, recent_media):
        mediaStr = str(recent_media)
        ID = mediaStr[mediaStr.find('Media: ')+7:]
        return ID

    # Gets username from JSON data
    def GetUsername(self, decodedData):
        try:
            return decodedData['data']['user']['username']
        except TypeError:
            return "Can't get username"
    
    # Gets caption text from JSON data
    def GetCaptionText(self, decodedData):
        try:
            return decodedData['data']['caption']['text']
        except TypeError:
            return "Can't get caption text"
        
    # Checks for duplicated user to ensure only 1 user is loved     
    def CheckUserDuplicates(self, username):
        try:
            userFile = open(self.USERNAMEFILE, 'r')
            for name in userFile.read().splitlines():
                if username == name:
                    return True    
            return False
        except IOError:
            open(self.USERNAMEFILE, 'w').close()
            return False
        
    # Gets media data from JSON data
    def GetMediaDataRaw(self, data):
        mediaID = self.GetMediaID(data)
        decodedData = self.DecodeJSONData(self.TAGURL % (mediaID, access_token))
        return decodedData
    
    # Main function
    def DoAutoLove(self, doRealLove):
        while True:
            # Gets random keywords to search
            tag_name = self.keywords.RandomWords()
            
            # Gets the media with the keyword in it
            recent_media = api.tag_recent_media(count = 1, tag_name = tag_name)
           
            # Gets the data from the media
            data = self.GetMediaDataRaw(recent_media[0][0])
           
            # Gets username from the data
            username = self.GetUsername(data)
            
            # Check id user exist in text file
            if self.CheckUserDuplicates(username) == True or username == "presentappco":
                print("AutoLoveTag - Same username, finding new user")
                continue
            
            print("AutoLoveTag - Found user!")
            
            # Gets the media id
            mediaID = self.GetMediaID(recent_media[0][0])
            
            # Gets the caption text of the media
            caption = self.GetCaptionText(data)
            
            # True = real love, False = test love
            # Real love post
            if doRealLove == True:
                # Try catch statement to catch api rate limits
                try:
                    api.like_media(mediaID)
                except InstagramAPIError:
                    print("AutoLoveTag - Rate limit exceeded, waiting %s seconds before continuing" % self.ENDBUFFERTIME)
                    time.sleep(self.ENDBUFFERTIME)
                    print("AutoLoveTag - Finished waiting, continuing...")
                    continue
                
                # Try catch statement to catch strings that has the error UnicodeEncodeError when printing out
                try:
                    print("AutoLoveTag - Real Liked " + username + "-" + caption + "\n")
                except UnicodeEncodeError:
                    print("AutoLoveTag - Real Liked \n")
            # Test love post
            else:
                try:
                    print("AutoLoveTag - Test Liked " + username + "-" + caption + "\n")
                except UnicodeEncodeError:
                    print("AutoLoveTag - Test Liked \n")
                
                self.WriteNameToFile(username)
                self.keywords.AddKeywordsToDict(tag_name, 1)
                self.TagLog.reset_log()
                
                for key, value in self.keywords.keywordsDict.items():    
                    self.TagLog.create_timed_log(key + ": " + str(value))
            break
        
    # Clears data from likedUser text file      
    def ResetData(self):
        open(self.USERNAMEFILE, 'w').close()
                
    def AutoLoveMain(self):
        currentTime = 0
        
        # 50 loves
        MaxLove = 30
        # Per hour 
        MaxTimeLimit = 3600
        # After an hour buffer time before restarting
        EndBufferTime = 60  
        
        # Buffer time between each favorite
        InBetweenTime = MaxTimeLimit / MaxLove 
        
        # Infinite loop
        while True:
            if currentTime < MaxTimeLimit:
                currentTime += InBetweenTime
            else:
                print("AutoLoveTag - " + str(MaxTimeLimit) + " seconds up, waiting " + str(EndBufferTime) + " seconds before continuing")
               
                #Real-time waiting 
                time.sleep(EndBufferTime)
                
                print ("AutoLoveTag - Resetting data...") 
                
                #Clear liked user names from text file (likedUser.txt)
                self.ResetData() 
                
                currentTime = 0
                
                print ("AutoLoveTag - Resetting done, continuing...") 
                
            #False for test like, True for real like
            self.DoAutoLove(False)
            
            print ("AutoLoveTag - Waiting " + str(InBetweenTime) + " seconds before continuing")
            
            #Real-time waiting 
            time.sleep(InBetweenTime) 
            
            if self.TagLog.timesup == True:
                self.TagLog.timesup = False
                self.keywords.ResetKeywordsDict()

            print ("AutoLoveTag - Waiting done, continuing... \n") 
            
if __name__ == "__main__":
    autoLove = AutoLove()
    
    autoLove.AutoLoveMain()
        
