from skimage import exposure
import numpy as np

def equalizing(image):
    p2, p98 = np.percentile(image, (2, 98))
    image_rescale = exposure.rescale_intensity(image, in_range=(p2, p98))
    image_eq = exposure.equalize_hist(image_rescale)
    image_adapt = exposure.equalize_adapthist(image_eq, clip_limit=0.03)
    return image_adapt