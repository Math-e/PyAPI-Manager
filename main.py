import re
import json
import shutil
from requests import get
from sys import argv
from pathlib import Path
try:
  from tqdm import tqdm
except ModuleNotFoundError:
    print("tqdm not installed")

class Session:
  def __init__(self, link: str, images: bool = True, videos: bool = False, attachments: bool = True, postLimit: int = 10):
    self.downloadImages = images
    self.downloadVideos = videos
    self.downloadAttachments = attachments
    self.postLimit = postLimit
    self.downloadedPosts = 0
    self.downloadedFiles = 0
    self.downloadedData = 0
    self.baseUrl = re.match(r"^https:\/\/\w*\.\w*\/", link).group()
    self.service_user = re.match(r"^https:\/\/[\w\.]*\/(\w*)\/user\/(\w*)\/?", link)
    self.service = self.service_user.group(1)
    self.creator = self.service_user.group(2)
    post = re.match(r".*\/post\/(\w*)/?", link)
    if post:
      self.post = post.group(1)

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
  
  # tqdm is optional module
  if 'tqdm' in globals():
    with tqdm.wrapattr(r.raw, "read", total=filesize, desc="")as raw:
      with open(path, 'wb') as output:
        shutil.copyfileobj(raw, output)

  else:
    with open(path, 'wb') as output:
      output.write(r.content)

  # checking download ok
  if r.status_code == 200:
    # increasing session stats
    s.downloadedFiles += 1
    s.downloadedData += filesize

    return True

  else:
    print(f'Error downloading. Code {r.status_code}')
    return None


def getApi(link):
  r = get(link)
  if r.status_code == 200:
    return r.json()
  else:
    print(f'Error accessing {link}')
    

class Creator:
  def __init__(self, s: Session):
    baseUrl = s.baseUrl
    service = s.service
    id = s.creator
    self.id = id
    self.service = service
    self.urlPosts = f"{baseUrl}api/v1/{service}/user/{id}"
    self.urlProfile = f"{baseUrl}api/v1/{service}/user/{id}/profile"
    self.urlBrowser = f"{baseUrl}{service}/user/{id}"
    # grab new info from profile url
    if not hasattr(self, 'info'):
      self.info = self.getData()
    self.savePath = Path(f"downloads/{self.info['name']} ({service})/")
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
            print(f"Post {post['id']} from {self.info['name']} already downloaded")
        else:
          print(f'{s.postLimit} posts limit reached')
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
    self.url = f"{baseUrl}api/v1/{creator.service}/user/{creator.id}/post/{self.id}"
    self.urlBrowser = f"{baseUrl}{creator.service}/user/{creator.id}/post/{self.id}"

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

        print(f"Downloading from {self.creator.info['name']} - {media['name']}")
<<<<<<< HEAD
        mediaUrl = f"{baseUrl}/data{media['path']}"
=======
        mediaUrl = f"{media['server']}/data{media['path']}"
>>>>>>> 3637e7eef5798a3ceb0d4d79e4a4f0d6de01248b
        # media path is "DownloadDirectory/CreatorDirectory/PostId_MediaName.fmt"
        path = Path(self.creator.savePath, f"{self.id}_{media['name']}")
        downloadTry = downloadMedia(mediaUrl, path)

        if downloadTry:
          data['services'][self.creator.service][self.creator.id][self.id].append(media['name'])
          saveData()
        else:
          print("Couldn't download " + media['name'])
      else:
        print(f"{media['name']} from {self.creator.info['name']} already downloaded")
<<<<<<< HEAD
    
    for att in self.info['attachments']:
      if att['name'].split('.')[1] in ['gif', '.jpg', 'png', 'jpeg'] and s.downloadImages == True:
        download(att)
          
      elif att['name'].split('.')[1] in ['mp4', 'webm', 'mkv'] and s.downloadVideos == True:
        download(att)
=======
>>>>>>> 3637e7eef5798a3ceb0d4d79e4a4f0d6de01248b

      elif s.downloadAttachments == True:
        download(att)

    s.downloadedPosts += 1
    

<<<<<<< HEAD
def main(link: str):
  s = Session(link)

  if not s.service in data['services']:
    data['services'][s.service] = {}
  if not s.creator in data['services'][s.service]:
    data['services'][s.service][s.creator] = {}

  requestedCreator = Creator(s).getPosts(s.post)

  print(f'Session ended!\n{s.downloadedPosts} posts downloaded, transfered {s.downloadedMB}MB from {s.downloadedFiles} medias')

dataFile = Path('downloaded.json')
data = loadData()

if len(argv) > 1:
  for link in argv[1:]:
    main(link)
=======
def main(link):
  baseUrl = re.match(r"^https:\/\/\w*\.\w*\/", link).group()
  service_user = re.match(r"^https:\/\/[\w\.]*\/(\w*)\/user\/(\w*)\/?", link)
  service = service_user.group(1)
  creator = service_user.group(2)
  post = re.match(r".*\/post\/(\w*)/?", link)

  if post:
    post = post.group(1)

  if not service in data['services']:
    data['services'][service] = {}
  if not creator in data['services'][service]:
    data['services'][service][creator] = {}

  requestedCreator = Creator(creator, service).getPosts(post)

  print(f'Session ended!\n{s.downloadedPosts} posts downloaded, transfered {s.downloadedMB}MB from {s.downloadedFiles} medias')

dataFile = Path('downloaded.json')
s = Session()
data = loadData()

if len(argv) > 1:
  for arg in argv[1:]:
    main(arg)
>>>>>>> 3637e7eef5798a3ceb0d4d79e4a4f0d6de01248b
