from tumblpy import Tumblpy
import urllib.request as urllib2
import json, codecs
import time

# Get the final tokens from the database or wherever you have them stored
t = Tumblpy("aDnOPY0TMjGlvge1WXf9m7iYScGKwW39Lay7fVcPwOtyi0gI1j", "soipYkCzLZfFVgDTU9Sc1gujAPTtmaAQB3N10jWlo21r5ZVxgK",
            "g8KKgHnoZUnknbmnyCcghGZzMvIzH3VzdnXsMls0iDHbsWTeUF", "bgepJW6rZysdAivMGMvn9iRjVpcxw78JieY3KMJi0JMzv2lXta")

# Print out the user info, let's get the first blog url...
blog_url = t.post('user/info')
blog_url = str(blog_url['user']['blogs'][0]['url'])
#posts = t.get('posts', blog_url=blog_url)

class UserInfo:
    def __init__(self, name, postURL, postID, reblogKey):
        self.Name = name
        self.PostURL = postURL
        self.PostID = postID
        self.ReblogKey = reblogKey
        
class AutoLovePost:
    USERNAMEFILE = "likedUser.txt"
    
    # Writes followed user name into a file (followedUser.txt)
    def WriteNameToFile(self, username):
        userFile = open(self.USERNAMEFILE, 'a')
        userFile.write(username)
        userFile.write('\n')
        userFile.close()
    
    # Check if already liked user
    def CheckLikedStatus(self, username):
        try:
            userFile = open(self.USERNAMEFILE, 'r')
            for name in userFile.read().splitlines():
                if username == name:
                    return True    
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
    
    def GetBlogURL(self, blogURL):
        POSTURL = "http://api.tumblr.com/v2/blog/%s/posts?api_key=%s&notes_info=true" % (blogURL[blogURL.find('http://')+7:blogURL.find('.com/')+4], "aDnOPY0TMjGlvge1WXf9m7iYScGKwW39Lay7fVcPwOtyi0gI1j")
        return POSTURL
    
    def LikePost(self, postID, reblogKey):
        post = t.post('user/like', params={'id':postID, 'reblog_key':reblogKey})
        return post
    
    def DoAutoLove(self, doRealLove):
        MaxPostCount = 5
        CurrentPostCount = 0
        
        inBetweenTime = 120
        tempName = ""
        userBlogData = []
        postList = []
        userName = []
        
        blogURL = self.GetBlogURL(blog_url)
        decodedData = self.DecodeJSONData(blogURL)
        
        try:
            for user in decodedData['response']['posts'][0]['notes']:
                if user['type'] == 'like':
                    userBlogData.append(self.DecodeJSONData(self.GetBlogURL(user['blog_url'])))
        except KeyError:
            print("No user liked your post yet")
            return
        
        for userData in userBlogData:
            if userData['response']['total_posts'] == 0:
                print(userData['response']['blog']['name'] + " has no post yet")
                continue
            
            for user in userData['response']['posts']:
                if self.CheckLikedStatus(user['blog_name']) == True:
                    print("Already Liked %s's post!" % user['blog_name'])
                else:   
                    if tempName != user['blog_name']:
                        tempName = user['blog_name']
                        userName.append(tempName)
                        CurrentPostCount = 0
                        
                    if CurrentPostCount < MaxPostCount:
                        CurrentPostCount += 1
                    else:
                        if tempName == user['blog_name']:
                            continue
                    
                    postList.append(UserInfo(user['blog_name'], user['post_url'], user['id'], user['reblog_key']))
                
        for user in userName:
            self.WriteNameToFile(user)
  
        userName.clear()

        for post in postList:
            print("Waiting " + str(inBetweenTime) + " seconds before continuing") 
            time.sleep(inBetweenTime)
            if doRealLove == True:
                self.LikePost(post.PostID, post.ReblogKey)
                print("Real liked %s's post: %s\n" % (post.Name, post.PostURL))
            else:
                print("Test liked %s's post: %s\n" % (post.Name, post.PostURL))

    def AutoLoveMain(self):
        while True:
            self.DoAutoLove(True)
            
if __name__ == "__main__":
    autoLove = AutoLovePost()
    
    autoLove.AutoLoveMain()
    
    
    
    
    