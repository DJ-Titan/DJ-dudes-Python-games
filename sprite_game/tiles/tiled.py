# This has minimal support for Tiled files.

# 1. tsx files must be assembled from individual tiles (not a tilesheet that is cut down).
# If you have a tilesheet, you have to use a tool like 'split_image' (https://pypi.org/project/split-image/)
# to do so first, then build the .tsx from your collection of tiles.

# 2. Each tile in your .tsx file need to have the same square dimensions.

# 3. The .tmx file can only contain one .tsx tileset

# 4. All layers must be the same map dimensions

# 5. Each map has a drawable 'spaceman' layer, 'objects0', and 'background0' layer.  There 
# is also a 'collision' layer using the red tile but isn't drawn.  The objects and background 
# can have multiple layers, but they have to be suffixed with a number for their order:
# (background0 will be drawn before background1)  There is no limit to the number of background and objects 
# layers provided so ling as the first is enumerated 0 and incremented by 1 for each suffessive layer.

import xml.etree.ElementTree as ET
from pathlib import Path
from tiles.image_memoize import Base64ImageMemoizer
from io import StringIO
import pandas as pd
import numpy as np

class Tileset:
    __tree = None
    __root = None
    __tile_mapping = None
    __my_images = None
    tiles = None

    def __init__(self,file_path, tsx_file_name):
        self.__tree = ET.parse(file_path / tsx_file_name)
        self.__root = self.__tree.getroot()
        
        self.__my_images = Base64ImageMemoizer(file_path)
        self.__tile_mapping = {}
        self.tiles = {}
        print("Loading Tiles:")
        for tile in self.__root.iter('tile'):
            for image in tile.iter('image'):
                print (image.attrib['source'])
                self.__tile_mapping[tile.attrib['id']]=image.attrib['source']
                self.tiles[tile.attrib['id']]=self.__my_images.load(image.attrib['source'])
        

    def getTileDict(self):
        return self.__tiles

class Map:
    __tree = None
    __root = None
    __map_size = None #[rows, cols]
    __tileset_filename = None
    map_layers = {} # dict
    __df_background_layers = None # pd.Dataframe
    __df_object_layers = None # pd.Dataframe
    
    def __init__(self, file_path, tmx_file_name):
        self.__tree = ET.parse(file_path / tmx_file_name)
        self.__root = self.__tree.getroot()
        self.__map_size = [int(self.__root.attrib['height']), int(self.__root.attrib['width'])]
        for tileset in self.__root.iter('tileset'):
            self.__tileset_filename = tileset.attrib['source']
            for layer in self.__root.iter('layer'):
                layer_name = layer.attrib['name']
                for data in layer.iter('data'): # csv map data for each layer
                    self.map_layers[layer_name] = pd.read_csv(StringIO(data.text), header=None)
        self.__df_background_layers = pd.DataFrame(np.full((self.__map_size[0], self.__map_size[1]), None)) # Create empty dataframe with the size of the layer, but filled with None
        self.__df_object_layers = pd.DataFrame(np.full((self.__map_size[0], self.__map_size[1]), None)) # Create empty dataframe with the size of the layer, but filled with None

        print("Hello")

    def mixBackgrounds(self):
        """This method will take the background images provided and render them from back to front."""
        bg_layers = [element for element in list(self.map_layers.keys()) if 'background' in element]    
        for row in range(self.__map_size[0]):
            for col in range(self.__map_size[1]):
                self.__df_background_layers.loc[row,col] = [self.map_layers[layer].loc[row,col] for layer in bg_layers]

    def mixObjects(self):
        """This method will take the object layers provided and render them from back to front."""
        bg_layers = [element for element in list(self.map_layers.keys()) if 'objects' in element]    
        for row in range(self.__map_size[0]):
            for col in range(self.__map_size[1]):
                self.__df_object_layers.loc[row,col] = [self.map_layers[layer].loc[row,col] for layer in bg_layers]
                
    def getBackgroundLayer(self):
        return self.__df_background_layers
    
    def getObjectsLayer(self):
        return self.__df_object_layers

    def mixTwoLayerDFs(self, df1, df2):
        for row in range(self.__map_size[0]):
            for col in range(self.__map_size[1]):
                cell = df1.loc[row,col]+df2.loc[row,col] if isinstance(df2.loc[row,col], list) else df1.loc[row,col]+[df2.loc[row,col]]
                df1.loc[row,col]= cell
        return df1.copy()

    def removeBlankTiles(self, df_in):
        """The process of stacking tile layers into a list of tile numbers for each x/y position in order, can produce a lot of 0 values.  These mean that there should be no tile, so we will omit all 0 values from the gameboard layers"""
        for row in range(self.__map_size[0]):
            for col in range(self.__map_size[1]):     
                cell = df_in.loc[row,col]
                df_in.loc[row,col] = [int(i-1) for i in cell if i != 0]
        return df_in.copy()

def getWindow(df, center_row, center_col, rows, cols, empty_tile_id):
    """
    Slices the compiled map dataframe to a small set window that will be rendered by the table.
    params:
    df (pandas.DataFrame):  This is the dataframe that you wish to slice a window out of
    center_row (int):       This is the row number of the dataframe to center the window (positional row using .iloc) default=0
    center_row (int):       This is the column number of the dataframe to center the window (positional col using .iloc) default=1 (must be odd)
    rows (int):             Total number of rows in the window.  default=9 (must be odd)
    cols (int):             Total number of columns in the window.  default=9
    empty_tile_id (int):    This is the id of a blank tile.  Used to fill empry areas in the window
    """
    if rows%2==0:
        raise ValueError("rows argument must be odd")
    if cols%2==0:
        raise ValueError("cols argument must be odd")

    start_row_offset = int((rows-1)/2)
    start_col_offset = int((cols-1)/2)

    start_row = center_row-start_row_offset
    start_col = center_col-start_col_offset

    df_out = pd.DataFrame.from_records([[[empty_tile_id]]*cols]*rows)
    for orig_row, new_row in zip(range(start_row, start_row+rows,1), range(rows)):
        for orig_col, new_col in zip(range(start_col, start_col+cols,1), range(cols)):
            if ((orig_row<df.shape[0])&(orig_row>=0)&(orig_col<df.shape[1])&(orig_col>=0)):
                df_out.iloc[new_row, new_col] = df.iloc[orig_row,orig_col]
            else:
                df_out.iloc[new_row, new_col] = [empty_tile_id]

    return df_out.copy()


if __name__=='__main__':
    www_dir = Path(__file__).parent / "www"
    tiles_dir = www_dir / "tiles"
    ship_tiles = Tileset(tiles_dir, 'ShipTiles.tsx')
    empty_tile_id = 6

    #tiled_project_dir = Path(__file__).parent / "tiled_project"
    my_map = Map(www_dir, 'ShipMap.tmx')
    my_map.mixBackgrounds()
    my_map.mixObjects()
    df_back_fore = my_map.mixTwoLayerDFs(my_map.getBackgroundLayer(),my_map.getObjectsLayer())
    df_final = my_map.mixTwoLayerDFs(df_back_fore, my_map.map_layers['spaceman'])
    df_final = my_map.removeBlankTiles(df_final)
    df_window = getWindow(df_final, 2, 3, 5, 3, empty_tile_id)
    print("base64",ship_tiles.tiles[str(int(df_window.iloc[0,0][0]))][0])
    print("datatype",ship_tiles.tiles[str(int(df_window.iloc[0,0][0]))][1])

