# -*- coding: utf-8 -*-
import urllib.request as urllib2
import json, codecs, time
import Logging, Configuration, threading
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError


config = Configuration.Configuration('config.ini')
access_token = config.AccessToken
client_id    = config.ClientID
redirect_uri = "https://presentapp.co/"
api = InstagramAPI(access_token=access_token)

# A class to automate following users that followed you     
class AutoFollow:
    USERNAMEFILE = "followedUser.txt"
    InBetweenTime = 180
    FollowerCount = 0
    
    UFLog = Logging.TimedLogging("UFLog", 1)
    UFLog.start()
    
    # Writes followed user name into a file (followedUser.txt)
    def WriteNameToFile(self, username):
        userFile = open(self.USERNAMEFILE, 'a')
        userFile.write(username)
        userFile.write('\n')
        userFile.close()
    
    # Check if already followed user
    def CheckFollowedStatus(self, username):
        try:
            userFile = open(self.USERNAMEFILE, 'r')
            for name in userFile.read().splitlines():
                if username == name:
                    userFile.close()
                    return True  
            
            userFile.close()  
            return False
        except IOError:
            open(self.USERNAMEFILE, 'w').close()
            return False
     
    # Convert URL to JSON data   
    def DecodeJSONData(self, url):
        response = urllib2.urlopen(url)
        reader = codecs.getreader("utf-8")
        decodedData = json.load(reader(response)) 
        return decodedData

    # Main auto follow function
    def DoAutoFollow(self, doRealFollow):
        # To authorize of basic, liking, following and commenting
        #webbrowser.open('https://instagram.com/oauth/authorize/?client_id=%s&redirect_uri=%s&response_type=token&scope=likes+relationships+comments+basic' % (client_id, redirect_uri))
        
        #USERURL = "https://api.instagram.com/v1/users/search?q=%s&access_token=" + access_token
        USERURL     = "https://api.instagram.com/v1/users/%s?access_token=" + access_token
        FOLLOWERURL = "https://api.instagram.com/v1/users/%s/followed-by?count=%s&access_token=" + access_token 
        
        # Gets own user id
        ownID = access_token[:access_token.find('.')]
        ownProfile = self.DecodeJSONData(USERURL % ownID)
        
        ownFollowerCount = ownProfile['data']['counts']['followed_by']
        # Gets list of user that has followed you
        followerData = self.DecodeJSONData(FOLLOWERURL % (ownID, ownFollowerCount))
        
        # Looping through each user data from the list
        for user in followerData['data']:
            # Gets username from user data
            username = user['username']
            userID   = user['id']

            # Check if user exist in the text file
            # If it exist, it will loop to next user
            # If it doesn't exist, continue
            if self.CheckFollowedStatus(username) == True:
                print("AutoFollow - Already followed " + username)
                continue
              
            print("AutoFollow - Waiting %s seconds before continuing." % self.InBetweenTime)
            time.sleep(self.InBetweenTime)
            print("AutoFollow - Done waiting, continuing...")
              
            # True = real follow, False = test follow
            # Real follow user
            if doRealFollow == True:
                api.follow_user(user_id=userID)
                print("AutoFollow - Real Followed " + username)
            # Test follow user
            else:
                print("AutoFollow - Test Followed " + username)   
        
            self.FollowerCount += 1
            self.WriteNameToFile(username)
            
            self.UFLog.create_timed_log(username)
            
            if self.UFLog.timesup == True:
                self.UFLog.create_timed_log(str(self.FollowerCount))
                self.UFLog.endtime = True
                self.FollowerCount = 0

    def AutoFollowMain(self):
        while True:
            self.DoAutoFollow(False)
     
    def TryAutoLove(self):
        EndBufferTime = 60 * 60
         
        try:
            self.AutoFollowMain()
        except InstagramAPIError:
            print("AutoFollow - Rate limit exceeded, waiting %s seconds before continuing" % EndBufferTime)
            time.sleep(EndBufferTime)
            print("AutoFollow - Finished waiting, continuing...")
            self.AutoFollowMain()

class FollowingUser(threading.Thread):
    
    FOLLOWINGFILE = "followingUser.txt"
    FollowingCount = 0
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
    
    # Convert URL to JSON data   
    def DecodeJSONData(self, url):
        response = urllib2.urlopen(url)
        reader = codecs.getreader("utf-8")
        decodedData = json.load(reader(response)) 
        return decodedData
    
    def GetFollowing(self):
        #USERURL = "https://api.instagram.com/v1/users/search?q=%s&access_token=" + access_token
        # Gets own user id
        USERURL      = "https://api.instagram.com/v1/users/%s?access_token=" + access_token
        FOLLOWINGURL = "https://api.instagram.com/v1/users/%s/follows?count=%s&access_token=" + access_token
        
        ownID = access_token[:access_token.find('.')]
        ownProfile = self.DecodeJSONData(USERURL % ownID)
        
        ownFollowingCount = ownProfile['data']['counts']['follows']
        # Gets list of user that has followed you
        followingData = self.DecodeJSONData(FOLLOWINGURL % (ownID, ownFollowingCount))
        
        # Looping through each user data from the list
        for user in followingData['data']:
            # Gets username from user data
            username = user['username']

            # Check if user exist in the text file
            # If it exist, it will loop to next user
            # If it doesn't exist, continue
            if self.CheckExistingFollowing(username) == True:
                print("AutoFollow - User already exist!")
                continue
            
            self.FollowingCount += 1
            
            self.WriteFollowingToFile(username)
            self.PFLog.create_timed_log(username)
            
            if self.PFLog.timesup == True:
                self.PFLog.create_timed_log(str(self.FollowingCount))
                self.PFLog.endtime = True
                self.FollowingCount = 0
                
    def DoGetFollowing(self):
        try:
            self.GetFollowing()    
        except InstagramAPIError:
            print("FollowingUser - Rate limit exceeded, waiting 15 minutes before continuing")
            time.sleep(15 * 60)
            print("FollowingUser - Finished waiting, continuing...")
            self.GetFollowing()    
            
    def run(self):
        while True:
            self.DoGetFollowing()
                              
if __name__ == "__main__":
    followingUser = FollowingUser()
    followingUser.start()
     
    autoFollow = AutoFollow()  
    autoFollow.TryAutoLove()
    
    