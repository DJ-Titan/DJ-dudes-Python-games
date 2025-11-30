from pathlib import Path
import base64

class Base64ImageMemoizer:
    __image_dict={}
    __path=None

    def __init__(self, path=None):
        """path is the Pathlib path that ends at a folder (presumably where all the images are)"""
        self.__path = path

    def load(self, filename):
        if filename in list(self.__image_dict.keys()):
            return (self.__image_dict[filename][0], self.__image_dict[filename][1])
        else:
            extension = filename.split('.')[-1]
            with open(self.__path / filename, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            self.__image_dict[filename]=[encoded_string, extension]
            return (encoded_string, extension)

if __name__=='__main__':
    www_dir = Path(__file__).parent / "www"
    my_images = Base64ImageMemoizer(www_dir)
    img_data, ext = my_images.load("tiles/Spaceman-light.gif")

    print(img_data)
    print(ext)

    img_data, ext = my_images.load("tiles/Spaceman-light.gif")

    print(img_data)
    print(ext)    

