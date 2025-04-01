import re
import json
import shutil
from requests import get
from sys import argv
from pathlib import Path
from tqdm import tqdm


class Session:
  def __init__(self, images: bool = True, videos: bool = False, attachments: bool = True, postLimit: int = 10):
    self.downloadImages = images
    self.downloadVideos = videos
    self.downloadAttachments = attachments
    self.postLimit = postLimit
    self.downloadedPosts = 0
    self.downloadedFiles = 0
    self.downloadedData = 0

  @property
  def downloadedMB(self):
    return round((self.downloadedData / 1024 / 1024), 2)

def dataTouch():
  default = {
    'services': {}
  }
  json.dump(default, dataFile.open('w'))

def loadData():
  if not Path.exists(dataFile):
    dataTouch()
  
  return json.load(dataFile.open('r'))

def saveData():
  json.dump(data, dataFile.open('w'))
  return True

def downloadMedia(link: str, path: Path):
  r = get(link, stream=True)
  filesize = int(r.headers.get("Content-Length"))
  
  with tqdm.wrapattr(r.raw, "read", total=filesize, desc="")as raw:
    with open(path, 'wb') as output:
      shutil.copyfileobj(raw, output)

  # checking download ok
  if r.status_code == 200:
    # increasing session stats
    s.downloadedFiles += 1
    s.downloadedData += filesize

    return True

  else:
    print('Error downloading')
    return None


def getApi(link):
  r = get(link)
  if r.status_code == 200:
    return r.json()
  else:
    print('Error accessing ' % link)
    

class Creator:
  def __init__(self, id: str, service: str):
    self.id = id
    self.service = service
    self.urlPosts = "%sapi/v1/%s/user/%s"%(baseUrl, service, id)
    self.urlProfile = "%sapi/v1/%s/user/%s/profile"%(baseUrl, service, id)
    self.urlBrowser = "%s%s/user/%s"%(baseUrl, service, id)
    # grab new info from profile url
    if not hasattr(self, 'info'):
      self.info = self.getData()
    self.savePath = Path('downloads/%s (%s)/'%(self.info['name'], service))
    Path.mkdir(self.savePath, exist_ok=True)
    self.posts = []

  def getData(self):
    return getApi(self.urlProfile)

  # downloads the first (s.postLimit) posts, or a specific post if sent
  def getPosts(self, postId = None):
    if postId:
      self.getPost(postId)
    else:
      allPosts = getApi(self.urlPosts)
      for post in allPosts:
        # check post download limit
        if s.downloadedPosts < s.postLimit:
          # check post already downloaded
          if not post['id'] in data['services'][self.service][self.id]:
            # send the post params to the function, so it doesn't need to call API again
            self.getPost(post['id'])
          else:
            print('Post %s from %s already downloaded'%(post['id'], self.info['name']))
        else:
          print('%s posts limit reached' % s.postLimit)
          break
      

  def getPost(self, id):
    self.posts.append(Post(id, self))

  def updateSave(self):
    data[self.service][self.id] = self.__dict__
    saveData()
  
  
class Post:
  def __init__(self, id: str, creator: Creator):
    self.id = id
    self.creator = creator
    self.url = "%sapi/v1/%s/user/%s/post/%s"%(baseUrl, creator.service, creator.id, self.id)
    self.urlBrowser = "%s%s/user/%s/post/%s"%(baseUrl, creator.service, creator.id, self.id)

    self.info = self.loadInfo()
    
    self.downloadMedia()

  def loadInfo(self):
    return getApi(self.url)

  def downloadMedia(self):
    # create post object
    if not self.id in data['services'][self.creator.service][self.creator.id]:
      data['services'][self.creator.service][self.creator.id][self.id] = []

    # unique function for videos and images
    def download(media):

      # check if media is already downloaded
      if media['name'] not in data['services'][self.creator.service][self.creator.id][self.id]:

        print('Downloading from %s - %s'%(self.creator.info['name'], media['name']))
        mediaUrl = "%s/data%s"%(media['server'], media['path'])
        # media path is "DownloadDirectory/CreatorDirectory/PostId_MediaName.fmt"
        path = Path(self.creator.savePath, "%s_%s"%(self.id, media['name']))
        downloadTry = downloadMedia(mediaUrl, path)

        if downloadTry:
          data['services'][self.creator.service][self.creator.id][self.id].append(media['name'])
          saveData()
        else:
          print("Couldn't download " + media['name'])
      else:
        print('%s from %s already downloaded'%(media['name'], self.creator.info['name']))


    if s.downloadImages == True:
      for img in self.info['previews']:
        download(img)
        
    if s.downloadVideos == True:
      for vid in self.info['videos']:
        download(vid)

    if s.downloadAttachments == True:
      for attach in self.info['attachments']:
        download(attach)

    s.downloadedPosts += 1
    



dataFile = Path('downloaded.json')

s = Session()

data = loadData()

link = argv[1]
baseUrl = re.match(r"^https:\/\/\w*\.\w*\/", link).group()
service_user = re.match(r"^https:\/\/[\w\.]*\/(\w*)\/user\/(\w*)\/?", link)
service = service_user.group(1)
creator = service_user.group(2)
post = re.match(r".*\/post\/(\w*)/?", link)

if post:
  post = post.group(1)

def main(): 
  if not service in data['services']:
    data['services'][service] = {}
  if not creator in data['services'][service]:
    data['services'][service][creator] = {}

  requestedCreator = Creator(creator, service).getPosts(post)

  print('Session ended!\n%s posts downloaded, transfered %sMB from %s medias'%(s.downloadedPosts, s.downloadedMB, s.downloadedFiles))


# TODO loop argv
main()
