from PIL import Image
from enum import Enum

IMG_DIR = 'images/'
def get_img(file:str, size:tuple[int,int]):
    return Image.open(IMG_DIR+file).resize(
        size, Image.LANCZOS)

def in_range(v, lb, ub):
    '''Return whether lb < v < ub'''
    return lb < v and v < ub

class Item(Enum):
    '''Items in the game'''
    ZERO = 0
    UNOPEN = -2

ITEM_IMG_FILES = {
    Item.ZERO: '0.png',
    Item.UNOPEN: 'unopen.png',
}
