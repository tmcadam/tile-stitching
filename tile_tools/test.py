import urllib2
from cStringIO import StringIO

from PIL import Image
import base64

with open("blank.png", 'rb') as f:
    image = f.read()
    print base64.b64encode(image)
