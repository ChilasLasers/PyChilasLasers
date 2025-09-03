import markdown
from lightgallery import LightGalleryExtension

print(markdown.markdown('![!description](/img/pic1.png)', extensions=[LightGalleryExtension()]))