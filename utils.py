import numpy as np
import numpy.ma as ma


def image_histogram_equalization(image, number_bins=256):
    image_histogram, bins = np.histogram(image.flatten(), number_bins, density=True)
    cdf = image_histogram.cumsum()  # cumulative distribution function
    cdf = 255 * cdf / cdf[-1]  # normalize

    # use linear interpolation of cdf to find new pixel values
    # TODO should it be better nearest neighbour?
    image_equalized = np.interp(image.flatten(), bins[:-1], cdf)

    return ma.masked_array(image_equalized.reshape(image.shape), mask=image.mask)
