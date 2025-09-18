from skimage.color import rgb2gray

def grayscaling(original):
    grayscale = rgb2gray(original)
    return grayscale