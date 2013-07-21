'''useful functions to process pictures of billiards

    image_process module provide functions to process pictures of billiards,
    and some function to help analyze pictures.
'''


import colorsys
import unittest
from PIL import Image, ImageDraw, ImageFilter
import PIL
from Crypto.SelfTest import SelfTestError

# default position and size of billiards in the target pictures
LEFT = 215
TOP = 130
WIDTH = 270
HEIGHT = 270


def set_default_position(left, top, width, height):
    '''set default position of the billiards in each image.
    We are assume billiards is at fixed position and the image is taked with
    fixed resolution and at fixed point, this will improve the process locate
    billiards in image, and easy to implemented in reality.
    '''
    global LEFT, TOP, WIDTH, HEIGHT
    LEFT = left
    TOP = top
    WIDTH = width
    HEIGHT = height

def get_default_position():
    '''return default position of the billiards in each image.
    '''
    global  LEFT, TOP, WIDTH, HEIGHT
    return (LEFT, TOP, WIDTH, HEIGHT)

def create_ellipse_mask_image(width, height, im=None):
    '''Create an image with given size, draw an ellipse at center of the image,
    all pixels outside the ellipse with value 0, and inside the ellipse with
    value 1.

    Args:
        width: width of the output image, should not less than 0.
        height: height of the output image, should not less than 0.
        im(option): instance of PIL.Image, should be the image with billiards
            in it, if im is not None, will mask every pixel with white color.

    Returns:
        An instance of class PIL.Image with model "1".
    Raises:
        AssertError: width < 0 or height < 0.
    '''
    assert width >= 0 and  height >= 0
    imOut = Image.new("1", (width, height) , 0)
    draw = ImageDraw.Draw(imOut, "1")
    draw.ellipse((0, 0, width, height), fill=1, outline=1)
    if im != None:
        assert isinstance(im, PIL.Image.Image) and im.size == (width, height)
        for x in range(width):
            for y in range(height):
                color = im.getpixel((x, y))
                if is_white_color(color):
                    imOut.putpixel((x, y), 0)
    return imOut

def is_white_color(color):
    if isinstance(color, tuple):
        h, l, s = colorsys.rgb_to_hls(color[0], color[1], color[2])
        return abs(s) < 0.60 and l > 128
    else:
        return color > 128

def cut_region_in_image(im, startX, startY, width, height):
    '''Cut region in the image.

    Args:
        im: an PIL.Image instance.
        startX, startY: start position of the region to be cut.
        width, height: size of the region to be cut.

    Returns:
        A new PIL.Image instance contains region of original image.

    Raises:
        AssertError: width <= 0 or height <= 0 or startX < 0 or startY < 0
    '''
    assert width > 0 and height > 0 and startX >= 0 and startY >= 0
    return im.crop((startX, startY, startX + width, startY + height))

def add_ellipse_mask_to_image(im, masked=False):
    '''Add mask to given image, use create_ellipse_mask_image to create mask.

    Args:
        im: install of PIL.Image

    Returns:
        A new PIL.Image instance with mask added.
    '''
    w, h = im.size
    im_ = None
    if masked:
        im_ = im
    imMask = create_ellipse_mask_image(w, h, im_)
    imOut = Image.composite(im, imMask.convert(im.mode), imMask)
    return imOut

def locate_billiards_in_image(im, background=1):
    '''locate position and size of the  billiards in the given image.

    Args:
        im: instance of PIL.Image, with billiards contented
        background(option): background color, 0 or 1, 1 represent white color,
            0 represent black color. It's suggested used white color as
            background, and use black 8 to locate billiards for first time,
            and remember the location for other billiards.

    Returns:
        (x,y,width,height) position and size of the billiards in the image.
    '''
    def reverse_color(v):
        if v == 1:
            return 0
        elif v == 0:
            return 1
        else:
            return 0
    im_01 = im.convert("1")
    if background == 1:
        im_01 = Image.eval(im_01, reverse_color)
    return im_01.getbbox()

def get_ellipse_histogram_of_image(im, masked=False):
    '''Get histogram of the image, NOT counter pixels outside the ellipse.

    Args:
        im: an instance of PIL.Image
        masked(option): NOT counter white pixels when set masked to True.
            default: True

    Returns:
        a list of integer indicate each band's histogram  of the given image.
        len(list) equal 256 * band_counter
    '''
    im_ = None
    if masked:
        im_ = im
    w, h = im.size
    imMask = create_ellipse_mask_image(w, h, im_)
    return im.histogram(imMask)

def smooth_histogram(histogram, filterLength=41):
    '''smooth histogram, use filter like (1,1,1,1,1)

    Args:
        histogram: a list with length % 256 == 0, and length >= 256
        filterLength: length of filter, the bigger value make more smooth
    Returns:
        the histogram, same one with the arguments.
    '''
    filter = list()
    for i in range(filterLength):
        filter.append(1)
    bands_count = len(histogram) / 256
    for i in range(bands_count):
        _filterList(histogram, filter, start=256 * i, end=256 * (i + 1))
    return histogram

def draw_ellipse_histogram_hsl(im, masked=False):
    assert str(im.mode) == "RGB"
    width, height = im.size
    for x in xrange(width):
        for y in xrange(height):
            r, g, b = im.getpixel((x, y))
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            im.putpixel((x, y), (int(h * 255), int(l), int(abs(s))))
    return draw_ellipse_histogram(im, masked)


def draw_ellipse_histogram(im, masked=False):
    '''draw histogram to a new image, use get_ellipse_histogram_of_image(im,masked)
    to get histogram of the image.

    Args:
        im: an instance of PIL.Image
        masked(option): NOT counter pixels outside the ellipse and white pixels when
            set masked to True. default: True

    Returns:
        an new instance of PIL.Image
    '''
    if str(im.mode) == "L":
        return _draw_ellipse_histogram_L(im, masked)
    assert str(im.mode) == "RGB"
    imOut = Image.new("RGB", (3 * 256, 120), "rgb(255,255,255)")
    draw = ImageDraw.Draw(imOut, "RGB")
    histogram = get_ellipse_histogram_of_image(im, masked)
    pixCountMaxR = 0
    pixCountMaxG = 0
    pixCountMaxB = 0
    for index in range(256):
        if histogram[index] > pixCountMaxR:
            pixCountMaxR = histogram[index ]
        if histogram[index + 256] > pixCountMaxG:
            pixCountMaxG = histogram[index + 256]
        if histogram[index + 512] > pixCountMaxB:
            pixCountMaxB = histogram[index + 512]
    for index in range(256):
        countR = histogram[index]
        countG = histogram[index + 256]
        countB = histogram[index + 512]
        ratioR = float(countR / float(pixCountMaxR))
        ratioG = float(countG / float(pixCountMaxG))
        ratioB = float(countB / float(pixCountMaxB))
        draw.line([(index, 100), (index, 100 - int(ratioR * 100))],
                  "rgb(255,0,0)")
        draw.line([(index + 256, 100), (index + 256, 100 - int(ratioG * 100))],
                  "rgb(0,255,0)")
        draw.line([(index + 512, 100), (index + 512, 100 - int(ratioB * 100))],
                  "rgb(0,0,255)")
    draw.line([(0, 100), (767, 100)], "rgb(125,125,125)")
    averageR, averageG, averageB = get_ellipse_average_RGB(im, masked)
    maxR, maxG, maxB = get_ellipse_max_count_RGB(im, masked)
    msg = "maxRGB(%d, %d, %d), averageRGB(%d, %d, %d)" % \
        (maxR, maxG, maxB, averageR, averageG, averageB)
    draw.text((50, 105), text=msg, fill="rgb(0,0,0)", font=None)
    return imOut

def _draw_ellipse_histogram_L(im, masked=False):
    '''draw histogram to a new image, use get_ellipse_histogram_of_image(im,masked)
    to get histogram of the image.

    Args:
        im: an instance of PIL.Image, im.mode == "L"
        masked(option): NOT counter pixels outside the ellipse and white pixels when
            set masked to True. default: True

    Returns:
        an new instance of PIL.Image
    '''
    assert str(im.mode) == "L"
    imOut = Image.new("L", (256, 120), 255)
    draw = ImageDraw.Draw(imOut, "L")
    histogram = get_ellipse_histogram_of_image(im, masked)
    pixelCountMax = 0.0;
    for index in range(256):
        if histogram[index] > pixelCountMax:
            pixelCountMax = histogram[index]
    for index in range(256):
        ratio = float(float(histogram[index]) / float(pixelCountMax))
        draw.line([(index, 100), (index, 100 - int(ratio * 100))], 0)
    draw.line([(0, 100), (255, 100)], 125)
    average = get_ellipse_average_bright(im, masked)
    max = get_ellipse_max_count_bright(im, masked)
    msg = "Max(%d),  Average(%d)" % (max, average)
    draw.text((1, 105), msg, 0)
    return imOut

def get_ellipse_average_bright(im, maksed=True):
    '''get average brightness of given image.

    Args:
        im: an instance of PIL.Image
        masked(option): NOT counter pixels outside the ellipse and white pixels when
            set masked to True. default: True

    Returns:
        average brightness of the given image.
    '''
    im = im.convert("L")
    histogram = get_ellipse_histogram_of_image(im, maksed)
    index = 0
    countPixels = 0
    for count in histogram:
        countPixels = countPixels + count
        index = index + 1
    averageBright = 0
    index = 0
    if countPixels == 0:
        return 0
    for count in histogram:
        averageBright = averageBright + float(index * count) / countPixels
        index = index + 1
    return  int(averageBright)


def get_ellipse_average_RGB(im, masked=False):
    '''get average value of each band (R,G,B) of given image.

    Args:
        im: an instance of PIL.Image, im.mode == "RGB"
        masked(option): NOT counter pixels outside the ellipse and white pixels when
            set masked to True. default: True

    Returns:
        (R,G,B): average value of band (R,G,B) of the given image.
    '''
    assert str(im.mode) == "RGB"
    histogram = get_ellipse_histogram_of_image(im, masked)
    countPixelsR = 0
    countPixelsG = 0
    countPixelsB = 0
    for index in range(256):
        countPixelsR = countPixelsR + histogram[index]
        countPixelsG = countPixelsG + histogram[index + 256]
        countPixelsB = countPixelsB + histogram[index + 512]
    averageBrightR = 0
    averageBrightG = 0
    averageBrightB = 0
    for index in range(256):
        if countPixelsR != 0:
            averageBrightR = averageBrightR + \
                float(index * histogram[index ]) / countPixelsR
        if countPixelsG != 0:
            averageBrightG = averageBrightG + \
                float(index * histogram[index + 256]) / countPixelsG
        if countPixelsB != 0:
            averageBrightB = averageBrightB + \
                float(index * histogram[index + 512]) / countPixelsB
    return int(averageBrightR), int(averageBrightG), int(averageBrightB)


def get_ellipse_max_count_bright(im, masked=False):
    '''get max count brightness of the given image, max count is the
    brightness that max count pixels have the same brightness.

    Args:
        im: an instance of PIL.Image
        masked(option): NOT counter pixels outside the ellipse and white pixels when
            set masked to True. default: True

    Returns:
        max count brightness of the given image.
    '''
    im = im.convert("L")
    histogram = get_ellipse_histogram_of_image(im, masked)
    maxBright = 0
    targetIndex = 0
    for index in range(256):
        if histogram[index] > maxBright:
            maxBright = histogram[index]
            targetIndex = index
    return targetIndex

def get_ellipse_max_count_RGB(im, masked=False):
    '''get max count value of each band (R,G,B) in the given image, max count
    is the brightness that max count pixels have the same brightness.

    Args:
        im: an instance of PIL.Image
        masked(option): NOT counter pixels outside the ellipse and white pixels when
            set masked to True. default: True

    Returns:
        (r,b,b): max count brightness of band (R,G,B) in the given image.
    '''
    assert str(im.mode) == "RGB"
    histogram = get_ellipse_histogram_of_image(im, masked)
    maxR = 0
    maxG = 0
    maxB = 0
    targetIndexR = 0
    targetIndexG = 0
    targetIndexB = 0
    for index in range(256):
        if histogram[index] > maxR:
            maxR = histogram[index]
            targetIndexR = index
        if histogram[index + 256] > maxG:
            maxG = histogram[index + 256]
            targetIndexG = index
        if histogram[index + 512] > maxB:
            maxB = histogram[index + 512]
            targetIndexB = index
    return targetIndexR, targetIndexG, targetIndexB

def _filterList(targetList, filter=(1, 1, 1), start=0, end=None):
    '''filter the give list.
    Use Convolution to process list.

    Args:
        targetList: the list to be filtered.
        filter(option): the filter used to make convolution, default=(1,1,1)
        start(option): start index(included) of targetList, default=0
        end(option): end index(not included) of targetList,default=len(targetList)
    '''
    assert isinstance(filter, tuple) or isinstance(filter, list)
    length = len(filter)
    assert length % 2 == 1
    if end == None:
        end = len(targetList)
    newList = []
    for i in range(length / 2):
        newList.append(targetList[0])
    newList.extend(targetList[start: end])
    for i in range(length / 2):
        newList.append(targetList[-1])
    allWeight = 0
    for i in range(length):
        allWeight = allWeight + filter[i]

    for i in xrange(start, end):
        v1 = newList[i - start : i + length - start]
        targetList[i] = _multiList(v1, filter) / allWeight

def _multiList(v1, v2):
    '''multiply two list/tuple
    multiple each value in v1 and v2, and sum them.

    Args:
        v1: first list/tuple, len(v1) == len(v2).
        v2: second list/tuple, len(v1) == len(v2).
    Returns:
        the produce of the multiply.
    '''
    assert len(v1) == len(v2)
    result = 0
    for i in range(len(v1)):
        result = result + v1[i] * v2[i]
    return result


def get_ellipse_color_features(im):
    '''get follow features of the ellipse:
        total pixels count: all pixels inside the ellipse
        white pixels count: all pixels inside the ellipse and is white color.
        most represented color(R,G,B) expect white.
    '''
    totalPixelCount = 0
    whitePixelCount = 0
    width, height = im.size
    imMask = create_ellipse_mask_image(width, height)
    for x in xrange(width):
        for y in xrange(height):
            if imMask.getpixel((x, y)) != 0:  # inside ellipse
                totalPixelCount = totalPixelCount + 1
                if  is_white_color(im.getpixel((x, y))):
                    whitePixelCount = whitePixelCount + 1
    r, g, b = get_ellipse_max_count_RGB(im, masked=True)

    return totalPixelCount, whitePixelCount, r, g, b



###############################################################################
# for unit test
###############################################################################
class ImageProcessTest(unittest.TestCase):
    def slow(f):
        f.slow = True
        return f

    def setUp(self):
        self._test_im = Image.open("../../../pictures/VGA/0_a.jpg")

    def tearDown(self):
        self._test_im = None

    def test_is_white_color(self):
        self.assertTrue(is_white_color((255, 255, 255)))
        self.assertTrue(is_white_color((200, 200, 200)))
        self.assertTrue(is_white_color((150, 150, 150)))
        self.assertFalse(is_white_color((255, 255, 0)))
        self.assertFalse(is_white_color((255, 0, 255)))
        self.assertFalse(is_white_color((0, 255, 255)))
        self.assertFalse(is_white_color((0, 0, 255)))
        self.assertFalse(is_white_color((255, 0, 0)))
        self.assertFalse(is_white_color((0, 255, 0)))

    def test_create_ellipse_mask_image(self):
        x, y, w, h = get_default_position()
        im = cut_region_in_image(self._test_im, x, y, w, h)
        create_ellipse_mask_image(w, h, im)

    def test_createEllipseMaskImage_0_0(self):
        create_ellipse_mask_image(0, 0)

    def test_createEllipseMaskImage_1_1(self):
        create_ellipse_mask_image(1, 1)

    def test_createEllipseMaskImage_640_640(self):
        create_ellipse_mask_image(640, 640)

    def test_createEllipseMaskImage_639_639(self):
        create_ellipse_mask_image(639, 639)

    def test_cutImage_0_0_0_0(self):
        self.assertRaises(AssertionError, cut_region_in_image, self._test_im, 0, 0, 0, 0)

    def test_cutImage_0_0_1_1(self):
        cut_region_in_image(self._test_im, 0, 0, 1, 1)

    def test_cutImage_160_50_640_640(self):
        cut_region_in_image(self._test_im, 160, 50, 640, 640)

    def test_cutImage_160_50_800_800(self):
        cut_region_in_image(self._test_im, 160, 50, 8000, 8000)

    def test_addEllipseMask(self):
        x, y, w, h = locate_billiards_in_image(self._test_im)
        im = cut_region_in_image(self._test_im, x, y, w, h)
        add_ellipse_mask_to_image(im)

    def test_locateEllipseInImage(self):
        global LEFT, TOP, WIDTH, HEIGHT
        self.assertEqual(locate_billiards_in_image(self._test_im) , (LEFT, TOP, WIDTH, HEIGHT))

    def test_getEllipseHistogramRGB(self):
        im = Image.new("RGB", (640, 640), "rgb(255,255,255)")
        self.assertEqual(get_ellipse_histogram_of_image(im)[255], 322838)

    def test_getEllipseHistogramL(self):
        im = Image.new("RGB", (640, 640), "rgb(255,255,255)")
        im = im.convert("L")
        self.assertEqual(get_ellipse_histogram_of_image(im)[255], 322838)

    def test_getEllipseAverageBright(self):
        im = cut_region_in_image(self._test_im, 160, 50, 640, 640)
        self.assertEqual(get_ellipse_average_bright(im), 127)

    def test_getEllipseAverageBright_White(self):
        im = Image.new("RGB", (640, 640), "rgb(255,255,255)")
        self.assertEqual(get_ellipse_average_bright(im), 255)

    def test_getEllipseAverageBright_Black(self):
        im = Image.new("RGB", (640, 640), "rgb(0,0,0)")
        self.assertEqual(get_ellipse_average_bright(im), 0)

    def test_drawEllipseHistogram(self):
        im = self._test_im.filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.SMOOTH_MORE)
        im = draw_ellipse_histogram(im)

    def test_drawEllipseHistogram_Bright(self):
        im = self._test_im.filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.SMOOTH_MORE)
        im = draw_ellipse_histogram(im.convert("L"))

    def test_getEllipseAverageRGB(self):
        im = cut_region_in_image(self._test_im, 160, 50, 640, 640)
        self.assertEqual(get_ellipse_average_RGB(im), (177, 119, 41))

    def test_getEllipseAverageRGB_White(self):
        im = Image.new("RGB", (640, 640), "rgb(255,255,255)")
        self.assertEqual(get_ellipse_average_RGB(im), (255, 255, 255))

    def test_getEllipseAverageRGB_Black(self):
        im = Image.new("RGB", (640, 640), "rgb(0,0,0)")
        self.assertEqual(get_ellipse_average_RGB(im), (0, 0, 0))

    def test_getEllipseMaxCountBright(self):
        im = cut_region_in_image(self._test_im, 160, 50, 640, 640)
        self.assertEqual(get_ellipse_max_count_bright(im), 173)

    def test_getEllipseMaxCountBright_0(self):
        im = Image.new("RGB", (640, 640), "rgb(0,0,0)")
        self.assertEqual(get_ellipse_max_count_bright(im), 0)

    def test_getEllipseMaxCountBright_255(self):
        im = Image.new("RGB", (640, 640), "rgb(255,255,255)")
        self.assertEqual(get_ellipse_max_count_bright(im), 255)

    def test_getEllipseMaxCountRGB(self):
        im = cut_region_in_image(self._test_im, 160, 50, 640, 640)
        self.assertEqual(get_ellipse_max_count_RGB(im), (240, 156, 0))

    def test_getEllipseMaxCountRGB_0(self):
        im = Image.new("RGB", (640, 640), "rgb(0,0,0)")
        self.assertEqual(get_ellipse_max_count_RGB(im), (0, 0, 0))

    def test_getEllipseMaxCountRGB_255(self):
        im = Image.new("RGB", (640, 640), "rgb(255,255,255)")
        self.assertEqual(get_ellipse_max_count_RGB(im), (255, 255, 255))

    def test_filterList(self):
        l = list(range(256))
        _filterList(l)
