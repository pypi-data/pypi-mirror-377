#! /usr/bin/env python3

"""ImagGe Quality Assessment for Digitisation batches

Johan van der Knijff

Copyright 2025, KB/National Library of the Netherlands

Image properties extraction module

"""
import os
import sys #remove, test only
import io
import logging
import base64
from lxml import etree
import PIL
from PIL import ImageCms
from PIL.TiffTags import TAGS as TAGS_TIFF
from PIL.ExifTags import TAGS as TAGS_EXIF, GPSTAGS, IFD
from . import jpegquality

def dictionaryToElt(name, dictionary):
    """Create Element object from dictionary, with recursion"""
    elt = etree.Element(name)

    for k, v in dictionary.items():
        if isinstance(v, dict):
            child = dictionaryToElt(str(k),v)
            elt.append(child)
        else:
            child = etree.Element(k)
            child.text = str(v)
        elt.append(child)

    return elt


def getBPC(image):
    """Return Bits per Component as a function of mode and components values"""
    mode_to_bpp = {"1": 1,
                   "L": 8,
                   "P": 8,
                   "RGB": 24,
                   "RGBA": 32,
                   "CMYK": 32,
                   "YCbCr": 24,
                   "LAB": 24,
                   "HSV": 24,
                   "I": 32,
                   "F": 32}

    bitsPerPixel = mode_to_bpp[image.mode]
    noComponents = len(image.getbands())

    if noComponents != 0  and isinstance(bitsPerPixel, int):
        bpc = int(bitsPerPixel/noComponents)
    else:
        bpc = -9999

    return bpc


def getProperties(file):
    """Extract properties and return result as Element object"""

    # Create element object to store all properties
    propertiesElt = etree.Element("properties")

    # Element to store exceptions at file level
    exceptionsFileElt = etree.Element("exceptions")

    # Create and fill descriptive elements
    fPathElt = etree.Element("filePath")
    fPathElt.text = file
    fNameElt = etree.Element("fileName")
    fNameElt.text = os.path.basename(file)
    fSizeElt = etree.Element("fileSize")
    fSizeElt.text = str(os.path.getsize(file))

    # Add to properies element
    propertiesElt.append(fPathElt)
    propertiesElt.append(fNameElt)
    propertiesElt.append(fSizeElt)

    # Read image
    try:
        im = PIL.Image.open(file)
        im.load()
        propsImageElt = getImageProperties(im)
        propertiesElt.append(propsImageElt)

    except Exception  as e:
        ex = etree.SubElement(exceptionsFileElt,'exception')
        ex.text = str(e)
        propertiesElt.append(exceptionsFileElt)
        logging.warning(("while opening image: {}").format(str(e)))
        return propertiesElt

    return propertiesElt


def getImageProperties(image):
    """Extract image properties and return result as Element object"""

    # Dictionary for storing image properties
    propsImage = {}
    # Element for storing image-level exceptions
    exceptionsImageElt = etree.Element("exceptions")

    propsImage['format'] = image.format
    width = image.size[0]
    height = image.size[1]
    propsImage['width'] = width
    propsImage['height'] = height
    propsImage['mode'] = image.mode
    noComponents = len(image.getbands())
    propsImage['components']= noComponents
    bitsPerComponent = getBPC(image)
    propsImage['bpc'] = bitsPerComponent

    if image.format == "JPEG":
        try:
            # Estimate JPEG quality using least squares matching
            # against standard quantization tables
            quality, rmsError, nse = jpegquality.computeJPEGQuality(image)
            propsImage['JPEGQuality'] = quality
            propsImage['NSE_JPEGQuality'] = nse
        except Exception as e:
            ex = etree.SubElement(exceptionsImageElt,'exception')
            ex.text = str(e)
            logging.warning(("while estimating JPEG quality from image: {}").format(str(e)))


    for key, value in image.info.items():

        if key == 'exif':
            # Skip any exif elements as Exif tags are added later
            pass
        elif key == 'photoshop':
            # Skip photoshop elements, because they tend to be large and I don't know how to
            # properly decode them
            pass
        elif isinstance(value, bytes):
            propsImage[key] = 'bytestream'
        elif key == 'dpi' and isinstance(value, tuple):
            propsImage['ppi_x'] = value[0]
            propsImage['ppi_y'] = value[1]
        elif key == 'jfif_density' and isinstance(value, tuple):
            propsImage['jfif_density_x'] = value[0]
            propsImage['jfif_density_y'] = value[1]
        elif isinstance(value, tuple):
            # Skip any other properties that return tuples
            pass
        else:
            propsImage[key] = value

    # ICC profile name and description
    iccFlag = False
    try:
        icc = image.info['icc_profile']
        iccFlag = True
    except KeyError:
        pass

    if iccFlag:
        try:
            iccProfile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            propsImage['icc_profile_name'] = ImageCms.getProfileName(iccProfile).strip()
            propsImage['icc_profile_description'] = ImageCms.getProfileDescription(iccProfile).strip()
        except Exception as e:
            ex = etree.SubElement(exceptionsImageElt,'exception')
            ex.text = str(e)
            logging.warning(("while extracting ICC profile properties from image: {}").format(str(e)))


    if image.format == "TIFF":
        # Create element object to store TIFF tags
        propsTIFFElt = etree.Element("tiff")

        # Iterate over TIFF tags, code adapted from:
        # https://stackoverflow.com/a/75357594/1209004 and
        # https://stackoverflow.com/a/46910779

        propsTIFF = {TAGS_TIFF[key] : image.tag[key] for key in image.tag.keys()}

        for k, d in propsTIFF.items():
            tag = k
            tiffElt = etree.Element(str(tag))

            # Don't include values of below tags
            if tag not in ['PhotoshopInfo', 'ICCProfile', 'IptcNaaInfo', 'XMP']:
                # extracted value is tuple, so reformat as spece-delimited string
                v = ''
                if tag not in ['XResolution', 'YResolution']:
                    for x in d:
                        v = v + ' ' + str(x)
                else:
                    try:
                        # In case of XResolution / YResolution tag, parse numerator and denominator
                        # values, and convert to resolution value
                        num = d[0][0]
                        den = d[0][1]
                        v = str(num/den)
                    except exception:
                        pass

                tiffElt.text = v.strip()
            propsTIFFElt.append(tiffElt)

    # Exif tags
    propsExif = image.getexif()
    propsExifElt = etree.Element("exif")

    # Iterate over various Exif tags, code adapted from:
    # https://stackoverflow.com/a/75357594/1209004

    for k, v in propsExif.items():
        tag = TAGS_EXIF.get(k, k)
        exifElt = etree.Element(str(tag))
        if tag not in ['XMLPacket', 'InterColorProfile', 'IPTCNAA', 'ImageResources']:
            # Don't include content of these tags as text
            exifElt.text = str(v)

        propsExifElt.append(exifElt)

    for ifd_id in IFD:
        # Iterate over image file directories
        # NOTE: this can result in duplicate Exif Tags. Example: Thumbnail image is implemented as 
        # separate IFD, with XResolution / YResolution tags whose values are different from
        # main resolution tags. Currently these are all lumped together in the output.
        try:
            ifd = propsExif.get_ifd(ifd_id)

            if ifd_id == IFD.GPSInfo:
                resolve = GPSTAGS
            else:
                resolve = TAGS_EXIF

            for k, v in ifd.items():
                tag = resolve.get(k, k)
                exifElt = etree.Element(str(tag))
                exifElt.text = str(v)
                propsExifElt.append(exifElt)
        except KeyError:
            pass
    
    # Read XMP metadata as string since dedicated getxmp function returns dictionary
    # that is difficult to work with for our purposes 
    # See: https://github.com/python-pillow/Pillow/issues/5076#issuecomment-2119966091
    # this only works for TIFF!
    if image.format == "TIFF":
        xmp = image.tag_v2[700].decode('utf-8')
        # Convert to Element object
        propsXMPElt = etree.fromstring(xmp)

    propsImageElt = dictionaryToElt('image', propsImage)
    if image.format == "TIFF":
        propsImageElt.append(propsTIFFElt)
    propsImageElt.append(propsExifElt)
    if image.format == "TIFF":
        propsImageElt.append(propsXMPElt)
    propsImageElt.append(exceptionsImageElt)

    return propsImageElt
