import os.path
from PIL import Image, ImageFilter
import BilliardsDistinguish
from BilliardsDistinguish.image_process import *
from BilliardsDistinguish.billiards_distinguish import *
from locale import str
from lib2to3.fixer_util import String
import PIL
import colorsys


PICTURE_DIR = "../pictures/VGA/"
set_default_position(215, 130, 265, 265)


# PICTURE_DIR = "../pictures/720p/"
# set_default_position(585, 165, 415, 415)


def locate_billiards_position():
    im_8 = PIL.Image.open(os.path.join(PICTURE_DIR, "8.jpg"))
    x, y, w, h = locate_billiards_in_image(im_8, 1)
    set_default_position(x, y, w, h)

def get_image():
    global PICTURE_DIR
    import os.path
    fileList = os.listdir(PICTURE_DIR)
    fileList.sort()
    for filename_ in fileList:
        if filename_.endswith(".jpg"):
            file_ = Image.open(os.path.join(PICTURE_DIR, filename_))
            yield filename_, file_

def process_image():
    for filename_, im in get_image():
        filename_mask = filename_.replace(".jpg", "") + "_mask.jpg"
        filename_histogram = filename_.replace(".jpg", "") + "_histogram.jpg"
        filename_histogram_masked = filename_.replace(".jpg", "") + "_histogram_masked.jpg"
        x, y, w, h = get_default_position()
        im_cut = cut_region_in_image(im, x, y, w, h)
        total_pixels, white_pixels, r, g, b = get_ellipse_color_features(im_cut)
        print "==================================\n" + filename_
        print get_billiards_number(float(white_pixels) / total_pixels, r, g, b)

#         im_mask = add_ellipse_mask_to_image(im_cut, False)
#         im_mask.save(filename_mask)
#         im_histogram = draw_ellipse_histogram_hsl(im_mask, False)
#         im_histogram.save(filename_histogram)
#         im_histogram_masked = draw_ellipse_histogram_hsl(im_mask, True)
#         im_histogram_masked.save(filename_histogram_masked)



def main():
    process_image()


if __name__ == "__main__":
    main()
