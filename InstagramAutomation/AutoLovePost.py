# -*- coding: utf-8 -*-
import urllib.request as urllib2
import urllib, json, codecs, time
import Logging, Configuration
from instagram.bind import InstagramAPIError
from instagram.client import InstagramAPI

config = Configuration.Configuration('config.ini')
access_token = config.AccessToken
client_id    = config.ClientID
redirect_uri = "http://presentapp.co"
api = InstagramAPI(access_token=access_token)

# A class for user info
class UserInfo:
    
    def __init__(self, username, userid, mediaText, mediaID, mediaURL):
        self.Username = username
        self.UserID = userid
        self.MediaText = mediaText
        self.MediaID = mediaID
        self.MediaURL = mediaURL

# A class to automate loving user's post that loves your post
# Limited to 2 user post            
class AutoLovePost:
    USERNAMEFILE = "likedPostUser.txt"
    CurrentMediaID = ""
    FollowerCount = 0
            
    LoveLog = Logging.TimedLogging("LLog", 1)
    LoveLog.start()
    
    # Writes liked user name into a file (likedUser.txt)
    def WriteNameToFile(self, userInfo):
        userFile = open(self.USERNAMEFILE, 'a')
        userFile.write(userInfo)
        userFile.write('\n')
        userFile.close()
        
    # Checks for duplicated user to ensure only 1 user is loved     
    def CheckUserDuplicates(self, username):
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
    
    # Gets username from a single line (e.g. User: Jason)
    def GetUserName(self, data):
        usernameStr = str(data)
        name = usernameStr[usernameStr.find("'username': ")+13:]
        return name
    
    # Get user data that liked your post
    def GetUserPostData(self, ownPostData, count):
        POSTLIKEURL = "https://api.instagram.com/v1/media/%s/likes?access_token=" + access_token
        userDataList = []
        
        if ownPostData['data'][0]['likes']['count'] == 0:
            return 0
            
        decodedData = self.DecodeJSONData(POSTLIKEURL % ownPostData['data'][0]['id'])
        
        for user in decodedData['data']:
            if self.CheckUserDuplicates(user['username']) == True:
                if user == decodedData['data'][-1]:
                    return 0
                continue
            
            POSTURL = "https://api.instagram.com/v1/users/%s/media/recent/?access_token=%s&count=%d" % (user['id'], access_token, count)
            try:
                decodedData = self.DecodeJSONData(POSTURL)
            except urllib.error.HTTPError:
                continue
            
            for post in decodedData['data']:
                try:
                    captiontext = post['caption']['text']
                except TypeError:
                    captiontext = "Can't get status text"
                     
                userDataList.append(UserInfo(post['user']['username'], post['user']['id'], captiontext, post['id'], post['link']))
                
        return userDataList

    # Main function
    def DoAutoLove(self, doRealLove):
        POSTURL = "https://api.instagram.com/v1/users/%s/media/recent/?access_token=" + access_token + "&count=1"
        
        inBetweenTime = 90
        EndBufferTime = 900
        likePost = False
        
        # Gets own user id
        ownID = access_token[:access_token.find('.')]
        # Gets own latest post
        ownPostData = self.DecodeJSONData(POSTURL % (ownID))  
        # Gets all user that loves own latest post
        # Returns a UserInfo list
        likersData = self.GetUserPostData(ownPostData, 2)
        
        # Check if there is user that has like own latest post
        if likersData != 0:
            # Loops through all user data
            for user in likersData:
                print("AutoLovePost - Waiting " + str(inBetweenTime) + " seconds before continuing")    
                time.sleep(inBetweenTime)
                print("AutoLovePost - Done waiting, continuing...")
                
                # True = real love, False = test love
                # Real love post
                if doRealLove == True:
                    # if likePost = False, it means the current post hasn't been loved yet
                    # It will loop through until the post has been loved
                    while likePost == False:
                        # Try catch statement to catch api rate limits
                        try:
                            api.like_media(user.MediaID)
                            likePost = True
                        except InstagramAPIError:
                            print("AutoLovePost - Rate limit exceeded, waiting %s seconds before continuing" % EndBufferTime)
                            time.sleep(EndBufferTime)
                            print("AutoLovePost - Finished waiting, continuing...")
                    
                    # Resetting likePost
                    likePost = False
                    
                    # Try catch statement to catch strings that has the error UnicodeEncodeError when printing out
                    try:
                        print("AutoLovePost - Real Loved: " + user.Username + "-" + user.MediaText + "\n")
                    except UnicodeEncodeError:
                        print("AutoLovePost - Real Loved \n")
                # Test love post
                else:
                    try:
                        print("AutoLovePost - Test Loved: " + user.Username + "-" + user.MediaText + "\n")
                    except UnicodeEncodeError:
                        print("AutoLovePost - Test Loved \n")
                        
                # Checking of current own post id with text file
                # Is to write the current own post id into a file
                if self.CheckUserDuplicates(ownPostData['data'][0]['id']) == False:
                    userFile = open(self.USERNAMEFILE, 'w')
                    userFile.write(ownPostData['data'][0]['id'])
                    userFile.write('\n')
                    userFile.close()
                    
                    # Is to write the current own post id into a log
                    self.LoveLog.create_timed_log(ownPostData['data'][0]['link'])
                
                self.FollowerCount += 1
                
                # Logging of users that has been loved
                self.LoveLog.create_timed_log(user.Username + ": " + user.MediaURL)    
                
                if self.LoveLog.timesup == True:
                    self.LoveLog.create_timed_log(str(self.FollowerCount))
                    self.LoveLog.endtime = True
                    self.FollowerCount = 0
            
                # try catch statement to check if it's the last post by a user
                try:   
                    if likersData[likersData.index(user)+1].Username != user.Username:
                        print("AutoLovePost - Last post by " + user.Username + ", continuing next user\n")
                        self.WriteNameToFile(user.Username)
                except IndexError:
                    print("AutoLovePost - Last post by " + user.Username + ", continuing next user\n")
                    self.WriteNameToFile(user.Username)
        # No user has liked yet
        else:
            print("AutoLovePost - No new user liked yet") 
       
    def DoAutoLoveMain(self):
        while True:
            self.DoAutoLove(True)
    
    # Main function
    def TryAutoLove(self):
        self.DoAutoLoveMain()
            
if __name__ == "__main__":
    autoLove = AutoLovePost()
    
    autoLove.TryAutoLove() 
