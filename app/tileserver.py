#!/usr/bin/env python
import StringIO

import gdal
import sys, os, tempfile
from gdalconst import GA_ReadOnly
from math import ceil, log10
import operator

tilesize = 256

zoom = 0
ix = 0
iy = 0

tempdriver = gdal.GetDriverByName( 'MEM' )
tiledriver = gdal.GetDriverByName( 'png' )

# =============================================================================
def writetile( data, dxsize, dysize, bands):
    tmp = tempdriver.Create('', tilesize, tilesize, bands=4)
    alpha = tmp.GetRasterBand(4)
    from numpy import zeros
    alphaarray = (zeros((dysize, dxsize)) + 255).astype('b')
    alpha.WriteArray( alphaarray, 0, tilesize-dysize )

    # (write data from the bottom left corner)
    tmp.WriteRaster( 0, tilesize-dysize, dxsize, dysize, data, band_list=range(1, bands+1))

    # ... and then copy it into the final tile with given filename
    output = StringIO.StringIO()
    tiledriver.CreateCopy(output, tmp, strict=0)
    contents = output.getvalue()
    output.close()

    return 0

if __name__ == '__main__':
    input_file = '/tmp/igem15-sw/app/ui/stage.jpg'

    gdal.AllRegister()

    dataset = gdal.Open( input_file, GA_ReadOnly )
    if dataset is None:
        raise Exception("Error opening file "+input_file)

    bands = dataset.RasterCount

    xsize = dataset.RasterXSize
    ysize = dataset.RasterYSize

    geotransform = dataset.GetGeoTransform()

    projection = dataset.GetProjection()

    # Python 2.2 compatibility.
    log2 = lambda x: log10(x) / log10(2) # log2 (base 2 logarithm)
    sum = lambda seq, start=0: reduce( operator.add, seq, start)

    # Zoom levels of the pyramid.
    maxzoom = int(max( ceil(log2(xsize/float(tilesize))), ceil(log2(ysize/float(tilesize)))))
    zoompixels = [geotransform[1] * 2.0**(maxzoom-zoom) for zoom in range(0, maxzoom+1)]
    tilecount = sum( [
        int( ceil( xsize / (2.0**(maxzoom-zoom)*tilesize))) * \
        int( ceil( ysize / (2.0**(maxzoom-zoom)*tilesize))) \
        for zoom in range(maxzoom+1)
    ] )

    rmaxsize = 2.0**(maxzoom-zoom)*tilesize

    if ix+1 == int( ceil( xsize / rmaxsize)) and xsize % rmaxsize != 0:
        rxsize = int(xsize % rmaxsize)
    else:
        rxsize = int(rmaxsize)

    # Read window left coordinate in pixels.
    rx = int(ix * rmaxsize)

    #for iy in range(0, int( ceil( ysize / rmaxsize))):

    # Read window ysize in pixels.
    if iy+1 == int( ceil( ysize / rmaxsize)) and ysize % rmaxsize != 0:
        rysize = int(ysize % rmaxsize)
    else:
        rysize = int(rmaxsize)

    # Read window top coordinate in pixels.
    ry = int(ysize - (iy * rmaxsize)) - rysize

    dxsize = int(rxsize/rmaxsize * tilesize)
    dysize = int(rysize/rmaxsize * tilesize)

    # Load raster from read window.
    data = dataset.ReadRaster(rx, ry, rxsize, rysize, dxsize, dysize)
    # Write that raster to the tile.
    writetile( data, dxsize, dysize, bands)