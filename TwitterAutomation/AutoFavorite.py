# -*- coding: utf-8 -*-
from tweepy import OAuthHandler
import time
import tweepy
from random import randint
import Logging, Configuration
         
#Authenticates user 
def Authenticate ():
    config = Configuration.Configuration('config.ini')
    #enter the corresponding information from your Twitter application:
    CONSUMER_KEY    = config.ConsumerKey
    CONSUMER_SECRET = config.ConsumerSecret  
    ACCESS_KEY      = config.AccessKey       
    ACCESS_SECRET   = config.AccessSecret    
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    #auth.secure = True
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return auth

api = tweepy.API(Authenticate ()) 
    
# A class for user info
# Currently needed is Screen_Name
class UserInfo:
    def __init__(self, SName, Name, UID, SID, Text):
        self.Screen_Name = SName
        self.Name = Name
        self.User_ID = UID
        self.Status_ID = SID
        self.Status_Text = Text

# A class that manages keywords from a file (keywords.txt)
# Can add more words into the file    
class Keywords:
    filename = open('keywords.txt', 'r')
    words = filename.read().splitlines()
    filename.close()
    
    keywords = ""
    
    keywordsDict = {}
    
    for word in words:
        keywordsDict[word] = 0
            
    # Returns respective word from text file when index is specified (0 = diary memories, 1 = video diary etc.)
    def IDToWords (self, num, precise):
        if precise:
            self.keywords = self.words[num]
            return '"' + self.words[num] + '"'
        else:
            self.keywords = self.words[num]
            return self.words[num]
    
    # Returns number to words in text file in array terms (Length - 1)
    def WordsLength (self):
        return len(self.words) - 1
    
    # Generates random index from the number of words
    def RandomWordsID (self, num = -1):
        if num == -1:
            listNum = randint(0, Keywords().WordsLength())
        else:
            listNum = num
        print("Keyword: " + self.words[listNum])
        return listNum
    
    def AddKeywordsToDict(self, word, num):
        for key, value in self.keywordsDict.items():
            if key == word:
                self.keywordsDict[key] = value + num
                
    def ResetKeywordsDict(self):
        for word in self.words:
            self.keywordsDict[word] = 0
                          
# A class to automate favoriting tweet
# Limited to 1 user (Checks for duplicated user)     
class AutoFav:
    
    USERNAMEFILE = 'favoriteUser.txt'
    maxTweetCount = 20
 
    FavCount = 0
    
    keywords = Keywords()
    FavLog = Logging.TimedLogging("FLog", 1)
    FavLog.start()
    
    # Writes favorited user name into a file (favoritedUser.txt)
    def WriteNameToFile(self, userInfo):
        userFile = open(self.USERNAMEFILE, 'a')
        userFile.write(userInfo.Screen_Name)
        userFile.write('\n')
        userFile.close()
     
    # Checks for duplicated user to ensure only 1 user is favorited     
    def CheckUserDuplicates(self, screenName):
        try:
            userFile = open(self.USERNAMEFILE, 'r')
            for name in userFile.read().splitlines():
                if screenName == name:
                    return True    
            return False
        except IOError:
            open(self.USERNAMEFILE, 'w').close()
            return False
    
    # Actual function to automate favorite tweet     
    def DoAutoFav(self, doRealFav):
        while True:    
            # Looping through tweets with specific keyword
            for tweet in tweepy.Cursor(api.search, q=self.keywords.IDToWords(self.keywords.RandomWordsID(), True), count=self.maxTweetCount, result_type="recent").items():     
                # Check if user exist in text file
                if self.CheckUserDuplicates(tweet.user.screen_name) == True:
                    continue
                
                # Setting user data into UserInfo
                userInfo = UserInfo(tweet.user.screen_name, tweet.user.name, tweet.user.id, tweet.id, tweet.text)

                # True = real favorite, False = test favorite
                # Real favorite tweet
                if doRealFav == True:
                    # Try catch statement to catch api rate limits
                    try:
                        api.create_favorite(tweet.id)
                        try:
                            print("AutoFav - Real Favorited " + userInfo.Screen_Name + "-" + userInfo.Status_Text)
                        except UnicodeEncodeError:
                            print("AutoFav - Real Favorited")
                    except tweepy.error.TweepError:
                        print("AutoFav - Rate exceeded, waiting 15 minutes before continuing")
                        time.sleep(15 * 60)
                        print("AutoFav - Done waiting, continuing...")
                        continue
                    
                    self.WriteNameToFile(userInfo)
                    self.FavLog.create_timed_log(self.keywords.keywords)
                # Test favorite tweet
                else:
                    self.WriteNameToFile(userInfo)
                    self.keywords.AddKeywordsToDict(self.keywords.keywords, 1)
                    self.FavLog.reset_log()
                    for key, value in self.keywords.keywordsDict.items():    
                        self.FavLog.create_timed_log(key + ": " + str(value))
                    
                    try:
                        print("AutoFav - Test Favorited " + userInfo.Screen_Name + "-" + userInfo.Status_Text)
                    except UnicodeEncodeError:
                        print("AutoFav - Test Favorited")
                        
                # Increment favorite count if there's such tweet        
                self.FavCount += 1
                break
            
            # Check if there's any favorite
            # If not, refind tweet
            if self.FavCount != 0:
                self.FavCount = 0
                break
            
            print("AutoFav - Refinding keyword...")
    
    # Clears data from favoritedUser text file      
    def ResetData(self):
        open(self.USERNAMEFILE, 'w').close()
        
    def AutoFavMain(self):
        currentTime = 0
        
        # 40 favorites
        MaxFavorite = 40   
        # Per hour 
        MaxTimeLimit = 3600
        # After an hour buffer time before restarting
        EndBufferTime = 60  
        
        # Buffer time between each favorite
        InBetweenTime = MaxTimeLimit / MaxFavorite 

        # Infinite loop
        while True:
            if currentTime < MaxTimeLimit:
                currentTime += InBetweenTime
            else:
                #Clear favorited user names from text file (favoritedUser.txt)
                self.ResetData() 
                 
                #Real-time waiting 
                time.sleep(EndBufferTime)
                currentTime = 0
                    
            #False for test favorite, True for real favorite
            self.DoAutoFav(False)
            
            print("AutoFav - Waiting %s seconds before continuing" % InBetweenTime)
            #Real-time waiting 
            time.sleep(InBetweenTime)  
            
            if self.FavLog.timesup == True:
                self.FavLog.timesup = False
                self.keywords.ResetKeywordsDict()
            
            print("AutoFav - Finished waiting, continuing\n")  
        
if __name__ == "__main__":
    autoFav = AutoFav()
         
    autoFav.AutoFavMain()
            