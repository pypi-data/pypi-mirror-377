import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler

class Uploader(AllMatchHandler):
  # upload the images to the cloud

  def resolve(self)->None:
    pass