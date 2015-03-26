from tumblpy import Tumblpy
import time
import Configuration

config = Configuration.Configuration('config.ini')

# Get the final tokens from the database or wherever you have them stored
t = Tumblpy(config.ConsumerKey, config.ConsumerSecret,
            config.OauthToken, config.OauthTokenSecret)

# Print out the user info, let's get the first blog url...
blog_url = t.post('user/info')
blog_url = blog_url['user']['blogs'][0]['url']
posts = t.get('posts', blog_url=blog_url)

class UserInfo:
    
    def __init__(self, name, blogURL):
        self.Name = name
        self.BlogURL = blogURL

class AutoFollow:
    USERNAMEFILE = "followedUser.txt"
    
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
                    return True    
            return False
        except IOError:
            open(self.USERNAMEFILE, 'w').close()
            return False
    
    def CreatePhotoPost(self, photoDir, caption):
        photo = open(photoDir, 'rb')
        post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': caption, 'data': photo})
        
        return post
        
    def DeletePost(self, postID):
        post = t.post('post/delete', blog_url=blog_url, params={'id':postID})
        return post
    
    def FollowUser(self, blogURL):
        follow = t.post('user/follow', params={'url': blogURL})
        return follow
    
    def UnFollowUser(self, blogURL):
        follow = t.post('user/unfollow', params={'url': blogURL})
        return follow
    
    def GetFollowers(self, blogURL):
        post = t.post('followers', blog_url=blogURL)
        return post
        
    def DoAutoFollow(self, doRealFollow):
        inBetweenTime = 180
        
        if len(self.GetFollowers(blog_url)['users']) == 0:
            print("No followers yet")
            return
        
        for user in self.GetFollowers(blog_url)['users']:
            if self.CheckFollowedStatus(user['name']) == False:
                print("Waiting %s seconds before continuing" % inBetweenTime)    
                time.sleep(inBetweenTime)
                print("Waiting done, continuing...")
            
                if doRealFollow == True:
                    self.FollowUser(user['url'])
                    print("Real Following: " + str(user['name']) + " " + str(user['url']))
                else:
                    print("Test Following: " + str(user['name']) + " " + str(user['url']))
                    
                self.WriteNameToFile(user['name'])
            else:
                print("Already followed " + user['name'])
    
    def AutoFollowMain(self):
        while True:
            self.DoAutoFollow(True)
            
#        self.CreatePhotoPost('capture.png', '#winstonyeu')        
#         postID = posts['posts'][0]['id']
#         print(self.DeletePost(postID))
        
if __name__ == "__main__":
    autoFollow = AutoFollow()
    
    autoFollow.AutoFollowMain()
    
    
    
    
    
    
    