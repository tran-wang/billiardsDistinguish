from PIL import Image, ImageChops, ImageDraw, ImageFilter
import unittest
import logging

Left = 160
Top = 50
width = 640
height = 640

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
    imOut = Image.composite( im, imMask.convert( im.mode ), imMask )
    return imOut

def locateEllipseInImage( im ):
    global Left, Top, width, height
    return  Left, Top, width, height

def getEllipseHistogram( im ):
    w, h = im.size
    imMask = createEllipseMaskImage( w, h )
    histogram = im.histogram( imMask )
    filter = list()
    for i in range( 41 ):
        filter.append( 1 )
    if str( im.mode ) == "L":
        _filterList( histogram, filter )
    elif str( im.mode ) == "RGB":
        _filterList( histogram, filter, start = 0, end = 256 )
        _filterList( histogram, filter, start = 256, end = 512 )
        _filterList( histogram, filter, start = 512, end = 768 )
    return histogram

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
    max = getEllipseMaxCountBright( im )
    msg = "Max(%d),  Average(%d)" % ( max, average )
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
    maxR, maxG, maxB = getEllipseMaxCountRGB( im )
    msg = "maxRGB(%d, %d, %d), averageRGB(%d, %d, %d)" % ( maxR, maxG, maxB, averageR, averageG, averageB )
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
    if countPixels == 0:
        return 0
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
        if countPixelsR != 0:
            averageBrightR = averageBrightR + float( index * histogram[index ] ) / countPixelsR
        if countPixelsG != 0:
            averageBrightG = averageBrightG + float( index * histogram[index + 256] ) / countPixelsG
        if countPixelsB != 0:
            averageBrightB = averageBrightB + float( index * histogram[index + 512] ) / countPixelsB
    return int( averageBrightR ), int( averageBrightG ), int( averageBrightB )


def getEllipseMaxCountBright( im ):
    im = im.convert( "L" )
    histogram = getEllipseHistogram( im )
    maxBright = 0
    targetIndex = 0
    for index in range( 256 ):
        if histogram[index] > maxBright:
            maxBright = histogram[index]
            targetIndex = index
    return targetIndex

def getEllipseMaxCountRGB( im ):
    assert str( im.mode ) == "RGB"
    histogram = getEllipseHistogram( im )
    maxR = 0
    maxG = 0
    maxB = 0
    targetIndexR = 0
    targetIndexG = 0
    targetIndexB = 0
    for index in range( 256 ):
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

def _filterList( targetList, filter = ( 1, 1, 1 ), start = 0, end = None ):
    assert isinstance( filter, tuple ) or isinstance( filter, list )
    length = len( filter )
    assert length % 2 == 1
    if end == None:
        end = len( targetList )
    newList = []
    for i in range( length / 2 ):
        newList.append( targetList[0] )
    newList.extend( targetList[start: end] )
    for i in range( length / 2 ):
        newList.append( targetList[-1] )
    allWeight = 0
    for i in range( length ):
        allWeight = allWeight + filter[i]

    for i in xrange( start, end ):
        v1 = newList[i - start : i + length - start]
        targetList[i] = _multiList( v1, filter ) / allWeight

def _multiList( v1, v2 ):
    assert len( v1 ) == len( v2 )
    result = 0
    for i in range( len( v1 ) ):
        result = result + v1[i] * v2[i]
    return result

################################################################################
# def removeReflectionPart( im ):
#    w, h = im.size
#    for x in xrange( w ):
#        for y in xrange( h ):
#            if _isLight( im.getpixel( ( x, y ) ) ):
#                im.putpixel( ( x, y ), ( 0, 0, 0 ) )
# 
# def _isLight( rgb = ( 1, 1, 1 ) ):
#    r, g, b = rgb
#    if r > 100 and g > 100 and b > 50\
#        and abs( r - g ) / float( max( r, g ) ) < 0.5\
#        and abs( r - b ) / float( max( r, b ) ) < 0.5\
#        and abs( g - b ) / float( max( g, b ) ) < 0.5:
#        return True
#    elif r > 50 and g > 50 and b > 50\
#        and abs( r - g ) / float( max( r, g ) ) < 0.1\
#        and abs( r - b ) / float( max( r, b ) ) < 0.1\
#        and abs( g - b ) / float( max( g, b ) ) < 0.1:
#        return True
#    else:
#        return False
################################################################################



###############################################################################
# for unit test
###############################################################################
class ImageProcessTest( unittest.TestCase ):
    def slow( f ):
        f.slow = True
        return f

    def setUp( self ):
        self._test_im = Image.open( "../../../input/_9.jpg" )

    def tearDown( self ):
        self._test_im = None

    def test_createEllipseMaskImage_0_0( self ):
        createEllipseMaskImage( 0, 0 )

    def test_createEllipseMaskImage_1_1( self ):
        createEllipseMaskImage( 1, 1 )

    def test_createEllipseMaskImage_640_640( self ):
        createEllipseMaskImage( 640, 640 )

    def test_createEllipseMaskImage_639_639( self ):
        createEllipseMaskImage( 639, 639 )

    def test_cutImage_0_0_0_0( self ):
        self.assertRaises( AssertionError, cutImage, self._test_im, 0, 0, 0, 0 )

    def test_cutImage_0_0_1_1( self ):
        cutImage( self._test_im, 0, 0, 1, 1 )

    def test_cutImage_160_50_640_640( self ):
        cutImage( self._test_im, 160, 50, 640, 640 )

    def test_cutImage_160_50_800_800( self ):
        cutImage( self._test_im, 160, 50, 8000, 8000 )

    def test_addEllipseMask( self ):
        x, y, w, h = locateEllipseInImage( self._test_im )
        im = cutImage( self._test_im, x, y, w, h )
        addEllipseMask( im )

    def test_locateEllipseInImage( self ):
        global Left, Top, width, height
        self.assertEqual( locateEllipseInImage( self._test_im ) , ( Left, Top, width, height ) )

    def test_getEllipseHistogramRGB( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseHistogram( im )[255], 322838 )

    def test_getEllipseHistogramL( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        im = im.convert( "L" )
        self.assertEqual( getEllipseHistogram( im )[255], 322838 )

    def test_getEllipseAverageBright( self ):
        im = cutImage( self._test_im, 160, 50, 640, 640 )
        self.assertEqual( getEllipseAverageBright( im ), 127 )

    def test_getEllipseAverageBright_White( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseAverageBright( im ), 255 )

    def test_getEllipseAverageBright_Black( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseAverageBright( im ), 0 )

    def test_drawEllipseHistogram( self ):
        im = self._test_im.filter( ImageFilter.SMOOTH_MORE ).filter( ImageFilter.SMOOTH_MORE )
        im = drawEllipseHistogram( im )

    def test_drawEllipseHistogram_Bright( self ):
        im = self._test_im.filter( ImageFilter.SMOOTH_MORE ).filter( ImageFilter.SMOOTH_MORE )
        im = drawEllipseHistogram( im.convert( "L" ) )

    def test_getEllipseAverageRGB( self ):
        im = cutImage( self._test_im, 160, 50, 640, 640 )
        self.assertEqual( getEllipseAverageRGB( im ), ( 177, 119, 41 ) )

    def test_getEllipseAverageRGB_White( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseAverageRGB( im ), ( 255, 255, 255 ) )

    def test_getEllipseAverageRGB_Black( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseAverageRGB( im ), ( 0, 0, 0 ) )

    def test_getEllipseMaxCountBright( self ):
        im = cutImage( self._test_im, 160, 50, 640, 640 )
        self.assertEqual( getEllipseMaxCountBright( im ), 173 )

    def test_getEllipseMaxCountBright_0( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseMaxCountBright( im ), 0 )

    def test_getEllipseMaxCountBright_255( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseMaxCountBright( im ), 255 )

    def test_getEllipseMaxCountRGB( self ):
        im = cutImage( self._test_im, 160, 50, 640, 640 )
        self.assertEqual( getEllipseMaxCountRGB( im ), ( 240, 156, 0 ) )

    def test_getEllipseMaxCountRGB_0( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(0,0,0)" )
        self.assertEqual( getEllipseMaxCountRGB( im ), ( 0, 0, 0 ) )

    def test_getEllipseMaxCountRGB_255( self ):
        im = Image.new( "RGB", ( 640, 640 ), "rgb(255,255,255)" )
        self.assertEqual( getEllipseMaxCountRGB( im ), ( 255, 255, 255 ) )

    def test_filterList( self ):
        l = list( range( 256 ) )
        _filterList( l )
