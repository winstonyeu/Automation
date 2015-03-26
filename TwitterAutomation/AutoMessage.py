# -*- coding: utf-8 -*-
from tweepy import OAuthHandler
import os.path
import time
import tweepy
import Logging
import threading
import Configuration

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
                           
class AutoDirectMsg:
    # Message
    DIRECTMESSAGE = "Hey there, thanks for following Present! Check our app at http://bit.ly/19dJ9D6 and let us know what you think! Cheers, Present Team"
    
    # Text file that will contain all sent message user
    USERNAMEFILE = 'followerUser.txt'
    
    # Count of all sent message user
    currentFollowerCount = 0
    
    # Buffer time before sending message
    InBetweenTime = 60
    
    # Direct message log
    DMLog = Logging.TimedLogging("DMLog", 1)
    DMLog.start()
    # User follow Present
    UFLog = Logging.TimedLogging("UFLog", 1)
    UFLog.start()
    
    # Check if message was sent to follower
    # It will read from the text file and compare names and see whether to send the message
    # It will only send the message once to each follower even if the user unfollows and follows back
    def CheckFollower (self, userName):
        if os.path.isfile(self.USERNAMEFILE) == False:
            open(self.USERNAMEFILE, 'w').close()
             
        # Only goes in once on 1st follower
        if len(open(self.USERNAMEFILE, 'r').read().splitlines()) == 0:
            return False
        else:
            for name in open(self.USERNAMEFILE, 'r').read().splitlines():
                if userName == name:
                    return True
               
            return False
    
    # Writes new follower name into the text file
    def WriteFollowerToFile(self, followerName):
        followerFile = open(self.USERNAMEFILE, 'a')
        followerFile.write(followerName)
        followerFile.write('\n')
        followerFile.close()
    
    # Sends message and store user name into the list
    def SendDirectMessage(self, userName):  
        api.send_direct_message(screen_name = userName, text = self.DIRECTMESSAGE)
    
    def ResetFollower(self, followerName):
        self.WriteFollowerToFile(followerName)
        
    # Function that does the follower checking and sending of message
    def AutoMessage(self, doRealMssage):
        # Gets all follower of PresentAppCo
        for AllFollowers in tweepy.Cursor(api.followers, screen_name="PresentAppCo").items():
            # Check if user exist in text file
            if self.CheckFollower(AllFollowers.screen_name) == True:
                print("Already sent to " + AllFollowers.screen_name)
                continue
            
            print("Waiting " + str(self.InBetweenTime) + " seconds before continuing")
            time.sleep(self.InBetweenTime)
            print("Finished waiting, continuing")
        
            #self.ResetFollower(AllFollowers.screen_name)
            
            # Logging of user that has followed Present
            self.UFLog.create_timed_log(AllFollowers.screen_name)
            
            # True = real message, False = test message
            # Real message user
            if doRealMssage == True:
                self.SendDirectMessage(AllFollowers.screen_name)
                self.WriteFollowerToFile(AllFollowers.screen_name)
                print("Real sent msg to %s" % AllFollowers.screen_name)
            # Test message user
            else: 
                # Logging of user that has been sent direct message
                self.WriteFollowerToFile(AllFollowers.screen_name)
                print("Test sent msg to %s" % AllFollowers.screen_name)
            
            self.DMLog.create_timed_log(AllFollowers.screen_name)
            break
      
    # Main function with limit checking
    # If there is a rate limit error, it will wait 15 minutes before continuing (Twitter API rate limits, 15 mins)         
    def DoAutoMsg(self):
        try:
            self.AutoMessage(False)
        except tweepy.error.TweepError:
            print("AutoMsg - Rate limit exceeded, waiting 15 minutes before continuing")
            time.sleep(15 * 60)
            print("AutoMsg - Finished waiting, continuing...")
            self.AutoMessage(False)
            
    def AutoMsgMain(self):
        while True:
            self.DoAutoMsg()

class FollowingUser(threading.Thread):
    
    FOLLOWINGFILE = "followingUser.txt"
    
    InBetweenTime = 60
    
    # Present follow user
    PFLog = Logging.TimedLogging("PFLog", 1)
    PFLog.start()
    
    # Writes new following name into the text file
    def WriteFollowingToFile(self, followingName):
        followingFile = open(self.FOLLOWINGFILE, 'a')
        followingFile.write(followingName)
        followingFile.write('\n')
        followingFile.close()
    
    # Check if following user exist in text file
    def CheckExistingFollowing (self, screenName):
        try:
            userFile = open(self.FOLLOWINGFILE, 'r')
            for name in userFile.read().splitlines():
                if screenName == name:
                    return True    
            return False
        except IOError:
            open(self.FOLLOWINGFILE, 'w').close()
            return False
        
    def GetFollowing(self):
        for friend in tweepy.Cursor(api.friends).items():
            if self.CheckExistingFollowing(friend.screen_name) == True:
                print(friend.screen_name + " already exist in text file")
                continue
            
#             print("FollowingUser - Waiting " + str(self.InBetweenTime) + " seconds before continuing")
#             time.sleep(self.InBetweenTime)
#             print("FollowingUser - Finished waiting, continuing")
               
            self.WriteFollowingToFile(friend.screen_name)
            self.PFLog.create_timed_log(friend.screen_name)
            
    def DoGetFollowing(self):
        try:
            self.GetFollowing()    
        except tweepy.TweepError:
            print("FollowingUser - Rate limit exceeded, waiting 15 minutes before continuing")
            time.sleep(15 * 60)
            print("FollowingUser - Finished waiting, continuing...")
            self.GetFollowing()    
            
    def run(self):
        while True:
            self.DoGetFollowing()
    
if __name__ == "__main__":
#     followingUser = FollowingUser()
#     followingUser.start()
    
    autoMsg = AutoDirectMsg()
    autoMsg.AutoMsgMain()
    