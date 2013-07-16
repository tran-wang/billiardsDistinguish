from PIL import Image, ImageChops, ImageDraw, ImageFilter
import unittest
import logging

Left = 160
Top = 50
width = 640
height = 640

InputDir = "../../../input/"

def createEllipseMaskImage( width, height ):
    assert width >= 0 and  height >= 0
    im = Image.new( "1", ( width, height ) , 0 )
    draw = ImageDraw.Draw( im, "1" )
    draw.ellipse( ( 0, 0, width, height ), fill = 1, outline = 1 )
    return im

def cutImage( im, startX, startY, width, height ):
    assert width > 0 and height > 0 and startX >= 0 and startY >= 0
    return im.crop( ( startX, startY, startX + width, startY + height ) )

def addEllipseMask( im ):
    w, h = im.size
    imMask = createEllipseMaskImage( w, h )
    return Image.composite( im, imMask.convert( im.mode ), imMask )

def locateEllipseInImage( im ):
    global Left, Top, width, height
    im = im.convert("1")
    
    return  Left, Top, width, height

def getEllipseHistogram( im ):
    w, h = im.size
    imMask = createEllipseMaskImage( w, h )
    return im.histogram( imMask )

def _drawEllipseHistogramL( im ):
    assert str( im.mode ) == "L"
    imOut = Image.new( "L", ( 256, 120 ), 255 )
    draw = ImageDraw.Draw( imOut, "L" )
    histogram = getEllipseHistogram( im )
    pixelCountMax = 0.0;
    for index in range( 256 ):
        if histogram[index] > pixelCountMax:
            pixelCountMax = histogram[index]
    for index in range( 256 ):
        ratio = float( float( histogram[index] ) / float( pixelCountMax ) )
        draw.line( [( index, 100 ), ( index, 100 - int( ratio * 100 ) )], 0 )
    draw.line( [( 0, 100 ), ( 255, 100 )], 125 )
    average = getEllipseAverageBright( im )
    max = getEllipseMaxBright( im )
    min = getEllipseMinBright( im )
    msg = "Max(%d), Min(%d), Average(%d)" % ( max, min, average )
    draw.text( ( 1, 105 ), msg, 0 )
    return imOut

def drawEllipseHistogram( im ):
    if str( im.mode ) == "L":
        return _drawEllipseHistogramL( im )
    assert str( im.mode ) == "RGB"
    imOut = Image.new( "RGB", ( 3 * 256, 120 ), "rgb(255,255,255)" )
    draw = ImageDraw.Draw( imOut, "RGB" )
    histogram = getEllipseHistogram( im )
    pixCountMaxR = 0
    pixCountMaxG = 0
    pixCountMaxB = 0
    for index in range( 256 ):
        if histogram[index] > pixCountMaxR:
            pixCountMaxR = histogram[index ]
        if histogram[index + 256] > pixCountMaxG:
            pixCountMaxG = histogram[index + 256]
        if histogram[index + 512] > pixCountMaxB:
            pixCountMaxB = histogram[index + 512]
    for index in range( 256 ):
        countR = histogram[index]
        countG = histogram[index + 256]
        countB = histogram[index + 512]
        ratioR = float( countR / float( pixCountMaxR ) )
        ratioG = float( countG / float( pixCountMaxG ) )
        ratioB = float( countB / float( pixCountMaxB ) )
        draw.line( [( index, 100 ), ( index, 100 - int( ratioR * 100 ) )], "rgb(255,0,0)" )
        draw.line( [( index + 256, 100 ), ( index + 256, 100 - int( ratioG * 100 ) )], "rgb(0,255,0)" )
        draw.line( [( index + 512, 100 ), ( index + 512, 100 - int( ratioB * 100 ) )], "rgb(0,0,255)" )
    draw.line( [( 0, 100 ), ( 767, 100 )], "rgb(125,125,125)" )
    averageR, averageG, averageB = getEllipseAverageRGB( im )
    maxR, maxG, maxB = getEllipseMaxRGB( im )
    minR, minG, minB = getEllipseMinRGB( im )
    msg = "maxRGB(%d, %d, %d), minRGB(%d, %d, %d), averageRGB(%d, %d, %d)" % ( maxR, maxG, maxB, minR, minG, minB, averageR, averageG, averageB )
    draw.text( ( 50, 105 ), text = msg, fill = "rgb(0,0,0)", font = None )
    return imOut


def getEllipseAverageBright( im ):
    im = im.convert( "L" )
    histogram = getEllipseHistogram( im )
    index = 0
    countPixels = 0
    for count in histogram:
        countPixels = countPixels + count
        index = index + 1
    averageBright = 0
    index = 0
    for count in histogram:
        averageBright = averageBright + float( index * count ) / countPixels
        index = index + 1
    return  int( averageBright )


def getEllipseAverageRGB( im ):
    assert str( im.mode ) == "RGB"
    histogram = getEllipseHistogram( im )
    countPixelsR = 0
    countPixelsG = 0
    countPixelsB = 0
    for index in range( 256 ):
        countPixelsR = countPixelsR + histogram[index]
        countPixelsG = countPixelsG + histogram[index + 256]
        countPixelsB = countPixelsB + histogram[index + 512]
    averageBrightR = 0
    averageBrightG = 0
    averageBrightB = 0
    for index in range( 256 ):
        averageBrightR = averageBrightR + float( index * histogram[index ] ) / countPixelsR
        averageBrightG = averageBrightG + float( index * histogram[index + 256] ) / countPixelsG
        averageBrightB = averageBrightB + float( index * histogram[index + 512] ) / countPixelsB
    return int( averageBrightR ), int( averageBrightG ), int( averageBrightB )


def getEllipseMaxBright( im ):
    im = im.convert( "L" )
    histogram = getEllipseHistogram( im )
    maxBright = 0
    for index in range( 256 ):
        if histogram[index] != 0 and index > maxBright:
            maxBright = index
    return maxBright

def getEllipseMaxRGB( im ):
    assert str( im.mode ) == "RGB"
    histogram = getEllipseHistogram( im )
    maxR = 0
    maxG = 0
    maxB = 0
    for index in range( 256 ):
        if histogram[index] != 0 and index > maxR:
            maxR = index
        if histogram[index + 256] != 0 and index > maxG:
            maxG = index
        if histogram[index + 512] != 0 and index > maxB:
            maxB = index
    return maxR, maxG, maxB


def getEllipseMinBright( im ):
    im = im.convert( "L" )
    histogram = getEllipseHistogram( im )
    minBright = 255
    for index in range( 256 ):
        if histogram[index] != 0 and index < minBright:
            minBright = index
    return minBright

def getEllipseMinRGB( im ):
    assert str( im.mode ) == "RGB"
    histogram = getEllipseHistogram( im )
    minR = 255
    minG = 255
    minB = 255
    for index in range( 256 ):
        if histogram[index] != 0 and index < minR:
            minR = index
        if histogram[index + 256] != 0 and index < minG:
            minG = index
        if histogram[index + 512] != 0 and index < minB:
            minB = index
    return minR, minG, minB


def createtemplateBalls():
    im0 = Image.new( "RGB", ( 640, 640 ), color = "rgb(255,255,255)" )
    im0 = addEllipseMask( im0 )
    im0.save( InputDir + "0.bmp" )
    drawEllipseHistogram( im0 ).save( InputDir + "0_histogram.jpg" )
    drawEllipseHistogram( im0.convert( "L" ) ).save( InputDir + "0_bright_histogram.jpg" )

    im1 = Image.new( "RGB", ( 640, 640 ), color = "rgb(255,255,0)" )
    im1 = addEllipseMask( im1 )
    im1.save( InputDir + "1.jpg" )
    drawEllipseHistogram( im1 ).save( InputDir + "1_histogram.jpg" )
    drawEllipseHistogram( im1.convert( "L" ) ).save( InputDir + "1_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im1, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im1.save( InputDir + "9.jpg" )
    drawEllipseHistogram( im1 ).save( InputDir + "9_histogram.jpg" )
    drawEllipseHistogram( im1.convert( "L" ) ).save( InputDir + "9_bright_histogram.jpg" )

    im2 = Image.new( "RGB", ( 640, 640 ), color = "rgb(0,0,255)" )
    im2 = addEllipseMask( im2 )
    im2.save( InputDir + "2.jpg" )
    drawEllipseHistogram( im2 ).save( InputDir + "2_histogram.jpg" )
    drawEllipseHistogram( im2.convert( "L" ) ).save( InputDir + "2_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im2, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im2.save( InputDir + "10.jpg" )
    drawEllipseHistogram( im2 ).save( InputDir + "10_histogram.jpg" )
    drawEllipseHistogram( im2.convert( "L" ) ).save( InputDir + "10_bright_histogram.jpg" )

    im3 = Image.new( "RGB", ( 640, 640 ), color = "rgb(255,0,0)" )
    im3 = addEllipseMask( im3 )
    im3.save( InputDir + "3.jpg" )
    drawEllipseHistogram( im3 ).save( InputDir + "3_histogram.jpg" )
    drawEllipseHistogram( im3.convert( "L" ) ).save( InputDir + "3_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im3, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im3.save( InputDir + "11.jpg" )
    drawEllipseHistogram( im3 ).save( InputDir + "11_histogram.jpg" )
    drawEllipseHistogram( im3.convert( "L" ) ).save( InputDir + "11_bright_histogram.jpg" )

    im4 = Image.new( "RGB", ( 640, 640 ), color = "rgb(128,0,128)" )
    im4 = addEllipseMask( im4 )
    im4.save( InputDir + "4.jpg" )
    drawEllipseHistogram( im4 ).save( InputDir + "4_histogram.jpg" )
    drawEllipseHistogram( im4.convert( "L" ) ).save( InputDir + "4_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im4, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im4.save( InputDir + "12.jpg" )
    drawEllipseHistogram( im4 ).save( InputDir + "12_histogram.jpg" )
    drawEllipseHistogram( im4.convert( "L" ) ).save( InputDir + "12_bright_histogram.jpg" )

    im5 = Image.new( "RGB", ( 640, 640 ), color = "rgb(255,128,0)" )
    im5 = addEllipseMask( im5 )
    im5.save( InputDir + "5.jpg" )
    drawEllipseHistogram( im5 ).save( InputDir + "5_histogram.jpg" )
    drawEllipseHistogram( im5.convert( "L" ) ).save( InputDir + "5_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im5, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im5.save( InputDir + "13.jpg" )
    drawEllipseHistogram( im5 ).save( InputDir + "13_histogram.jpg" )
    drawEllipseHistogram( im5.convert( "L" ) ).save( InputDir + "13_bright_histogram.jpg" )

    im6 = Image.new( "RGB", ( 640, 640 ), color = "rgb(0,255,0)" )
    im6 = addEllipseMask( im6 )
    im6.save( InputDir + "6.jpg" )
    drawEllipseHistogram( im6 ).save( InputDir + "6_histogram.jpg" )
    drawEllipseHistogram( im6.convert( "L" ) ).save( InputDir + "6_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im6, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im6.save( InputDir + "14.jpg" )
    drawEllipseHistogram( im6 ).save( InputDir + "14_histogram.jpg" )
    drawEllipseHistogram( im6.convert( "L" ) ).save( InputDir + "14_bright_histogram.jpg" )

    im7 = Image.new( "RGB", ( 640, 640 ), color = "rgb(128,0,0)" )
    im7 = addEllipseMask( im7 )
    im7.save( InputDir + "7.jpg" )
    drawEllipseHistogram( im7 ).save( InputDir + "7_histogram.jpg" )
    drawEllipseHistogram( im7.convert( "L" ) ).save( InputDir + "7_bright_histogram.jpg" )
    draw = ImageDraw.Draw( im7, mode = "RGB" )
    draw.ellipse( ( 90, 90, 512, 512 ), fill = "rgb(255,255,255)" )
    im7.save( InputDir + "15.jpg" )
    drawEllipseHistogram( im7 ).save( InputDir + "15_histogram.jpg" )
    drawEllipseHistogram( im7.convert( "L" ) ).save( InputDir + "15_bright_histogram.jpg" )

    im8 = Image.new( "RGB", ( 640, 640 ), color = "rgb(0,0,0)" )
    im8 = addEllipseMask( im8 )
    im8.save( InputDir + "8.jpg" )
    drawEllipseHistogram( im8 ).save( InputDir + "8_histogram.jpg" )
    drawEllipseHistogram( im8.convert( "L" ) ).save( InputDir + "8_bright_histogram.jpg" )


createtemplateBalls()
###############################################################################
# for unit test
###############################################################################
class ImageProcessTest( unittest.TestCase ):
    def slow( f ):
        f.slow = True
        return f

    def setUp( self ):
        self._im_2 = Image.open( InputDir + "_9.jpg" )

    def tearDown( self ):
        self._im_2 = None

    @slow
    def test_createtemplateBalls( self ):
        createtemplateBalls()

    def test_createEllipseMaskImage_0_0( self ):
        createEllipseMaskImage( 0, 0 )

    def test_createEllipseMaskImage_1_1( self ):
        createEllipseMaskImage( 1, 1 )

    def test_createEllipseMaskImage_640_640( self ):
        createEllipseMaskImage( 640, 640 )

    def test_createEllipseMaskImage_639_639( self ):
        createEllipseMaskImage( 639, 639 )

    def test_cutImage_0_0_0_0( self ):
        self.assertRaises( AssertionError, cutImage, self._im_2, 0, 0, 0, 0 )

    def test_cutImage_0_0_1_1( self ):
        cutImage( self._im_2, 0, 0, 1, 1 )

    def test_cutImage_160_50_640_640( self ):
        cutImage( self._im_2, 160, 50, 640, 640 )

    def test_cutImage_160_50_800_800( self ):
        cutImage( self._im_2, 160, 50, 8000, 8000 )

    def test_addEllipseMask( self ):
        x, y, w, h = locateEllipseInImage( self._im_2 )
        im_2_e = cutImage( self._im_2, x, y, w, h )
        im_2_e.save( InputDir + "_9_cut.jpg" )
        addEllipseMask( im_2_e ).save( InputDir + "_9_cut_mask.jpg" )

    def test_locateEllipseInImage( self ):
        global Left, Top, width, height
        self.assertEqual( locateEllipseInImage( self._im_2 ) , ( Left, Top, width, height ) )

    def test_getEllipseHistogramRGB( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseHistogram( im )[255], 322838 )

    def test_getEllipseHistogramL( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        im = im.convert( "L" )
        self.assertEqual( getEllipseHistogram( im )[255], 322838 )

    def test_getEllipseAverageBright( self ):
        im = cutImage( self._im_2, 160, 50, 640, 640 )
        self.assertEqual( getEllipseAverageBright( im ), 127 )

    def test_getEllipseAverageBright_White( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseAverageBright( im ), 255 )

    def test_getEllipseAverageBright_Black( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseAverageBright( im ), 0 )

    def test_drawEllipseHistogram( self ):
        im = self._im_2.filter( ImageFilter.SMOOTH_MORE ).filter( ImageFilter.SMOOTH_MORE )
        im = drawEllipseHistogram( im )
        im.save( InputDir + "_9_histogram.jpg" )

    def test_drawEllipseHistogram_Bright( self ):
        im = self._im_2.filter( ImageFilter.SMOOTH_MORE ).filter( ImageFilter.SMOOTH_MORE )
        im = drawEllipseHistogram( im.convert( "L" ) )
        im.save( InputDir + "_9_birght_histogram.jpg" )

    def test_getEllipseAverageRGB( self ):
        im = cutImage( self._im_2, 160, 50, 640, 640 )
        self.assertEqual( getEllipseAverageRGB( im ), ( 177, 119, 41 ) )

    def test_getEllipseAverageRGB_White( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseAverageRGB( im ), ( 255, 255, 255 ) )

    def test_getEllipseAverageRGB_Black( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseAverageRGB( im ), ( 0, 0, 0 ) )

    def test_getEllipseMaxBright( self ):
        im = cutImage( self._im_2, 160, 50, 640, 640 )
        self.assertEqual( getEllipseMaxBright( im ), 253 )

    def test_getEllipseMaxBright_0( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseMaxBright( im ), 0 )

    def test_getEllipseMaxBright_255( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseMaxBright( im ), 255 )

    def test_getEllipseMaxRGB( self ):
        im = cutImage( self._im_2, 160, 50, 640, 640 )
        self.assertEqual( getEllipseMaxRGB( im ), ( 255, 255, 241 ) )

    def test_getEllipseMaxRGB_0( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseMaxRGB( im ), ( 0, 0, 0 ) )

    def test_getEllipseMaxRGB_255( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseMaxRGB( im ), ( 255, 255, 255 ) )

    def test_getEllipseMinBright( self ):
        im = cutImage( self._im_2, 160, 50, 640, 640 )
        self.assertEqual( getEllipseMinBright( im ), 30 )

    def test_getEllipseMinBright_0( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseMinBright( im ), 0 )

    def test_getEllipseMinBright_255( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseMinBright( im ), 255 )

    def test_getEllipseMinRGB( self ):
        im = cutImage( self._im_2, 160, 50, 640, 640 )
        self.assertEqual( getEllipseMinRGB( im ), ( 55, 19, 0 ) )

    def test_getEllipseMinRGB_0( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseMinRGB( im ), ( 0, 0, 0 ) )

    def test_getEllipseMinRGB_255( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseMinRGB( im ), ( 255, 255, 255 ) )
