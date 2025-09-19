# -*- coding: utf-8 -*-

"""
Inspired from:
    - https://gis.stackexchange.com/questions/392695/is-it-possible-to-build-a-vrt-file-from-multiple-files-with-rasterio
    - https://pypi.org/project/rio-vrt/
"""

from typing import Union, Optional

import logging

import xml.etree.ElementTree
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

import datetime

import rasterio
from rasterio.shutil import copy as riocopy
from rasterio.io import MemoryFile

logger = logging.getLogger(__name__)


def build_vrt(src_files: Union[str, list[str]], bands: Union[None, int, list[int], list[list[int]]],
              out_filename: str,  dates: Optional[list[Optional[int]]] = None,
              value_unit: Optional[str] = None, scale_factor: Optional[float] = None) -> bool:
    """
    Build a VRT (Virtual Raster Dataset) from one or several files and one or several band numbers.
    Dates can optionally be provided, one date per band to extract (in %Y%m%d format).
    A value unit string can also be optionnally provided.
    Finaly, a scale factor can be provided, to be applied to every extracted band.
    Return True if the VRT was created successfully, and False otherwise.

    Parameters
    ----------
    src_files : Union[str, list[str]]
        List of files from which to take bands to build the VRT. If a single file and a list of
        bands are given, then the VRT consists of all the given bands from the given file.
    bands : Union[None, int, list[int], list[list[int]]]
        A list of list of band numbers, one list of band numbers for each source file, to
        extract to build the VRT. If None is given, all bands of all source_files are extracted.
        If a single band number is given, that band will be extracted from each source file. If a
        single source file and a list of band numbers is given, then those bands will be extracted
        from the source file.
    out_filename : str
        A relative path toward the filename of the output VRT (will be created if needed).
    dates : Optional[list[Optional[int]]], optional
        A list of dates in format %Y%m%d, one date per band to extract (in the same order).
        For example, for 30th July 2018 : "20180730"
        see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    value_unit : Optional[str], optional
        String to use as the unit name of the bands (for example "radian").
    scale_factor : Optional[float], optional
        A scale factor to be applied to every extracted band

    Returns
    -------
    bool
        True if the VRT has been created, False if there was an problem along the way.
    """
    if scale_factor is not None:
        scale_factor = float(scale_factor)
        assert isinstance(scale_factor, float), "scale_factor must be float"
    if isinstance(src_files, str):
        src_files = [src_files]
    # from now on src_files is a list[str]
    if len(src_files) == 0:
        logger.error("There should be at least 1 file to create a vrt.")
        return False
    if bands is None:
        bands = []
        for src in src_files:
            with rasterio.open(src) as dataset:
                bands.append(list(dataset.indexes))
    elif isinstance(bands, int):
        bands = [[bands] for _ in src_files]
    elif all(isinstance(band, int) for band in bands):
        if len(src_files) == 1:
            bands = [bands]
        else:
            bands = [[band] for band in bands]
    # from now on bands is a list[list[int]]
    # meaning one list of band numbers to extract for each source file of src_files
    if len(src_files) != len(bands):
        logger.error("number of scr_files and number of bands not matching, abort")
        return False
    if dates is None:
        dates = [None for band in bands for _ in band]
    if sum(len(_) for _ in bands) != len(dates):
        logger.error("number of bands and number of dates not matching, abort")
        return False
    # perform sanity check that all source files have the same width, height, crs and transform
    # using set to store the values of the files and check that the length of the set is 1
    # (meaning that a single value has been found across all files)
    width, height = set(), set()
    crs = set()
    transform = set()
    for src in src_files:
        with rasterio.open(src) as dataset:
            width.add(dataset.width)
            height.add(dataset.height)
            if dataset.crs is None:
                crs.add(None)
            else:
                crs.add(dataset.crs.to_string())
            transform.add(dataset.transform)
    if len(width) != 1:
        logger.error(f"conflicting dataset widths found {width}, abort")
        return False
    rasterXSize = width.pop()
    if len(height) != 1:
        logger.error(f"conflicting dataset heights found {height}, abort")
        return False
    rasterYSize = height.pop()
    if len(crs) != 1:
        logger.error(f"conflicting dataset crs found {crs}, abort")
        return False
    if len(transform) != 1:
        logger.error("conflicting dataset georeferencing transformation matrixes"
                     f" found {transform}, abort")
        return False
    # create the list of bands to build the vrt
    out_bands = []
    # iterate over src_files and bands, adding targeted bands to out_bands
    for src, target_bands in zip(src_files, bands):
        with rasterio.open(src) as dataset, MemoryFile() as memfile:
            # copy the dataset in the memoryfile using VRT driver
            riocopy(dataset, memfile.name, driver='VRT')
            # parse the content of the memoryfile into an xml tree
            vrt_xml: Element = xml.etree.ElementTree.fromstring(memfile.read().decode('utf-8'))
            for target_band in target_bands:
                # select all children elements that are VRTRasterBand and have an attribute band
                # equal to target_band
                found_bands = vrt_xml.findall(f"VRTRasterBand[@band='{target_band}']")
                if len(found_bands) == 0:
                    logger.error(f"did not find band {target_band} in file {src}, abort")
                    return False
                if len(found_bands) > 1:
                    logger.error(f"found multiple band {target_band} in file {src}, abort")
                    return False
                found_band = found_bands[0]
                out_bands.append(found_band)
    # create the root of the VRT XML
    out_xml = Element('VRTDataset', {"rasterXSize": str(rasterXSize),
                                     "rasterYSize": str(rasterYSize)})
    # if crs is not None, give the spatial reference system from the first source file to the output
    if crs.pop() is not None:
        with rasterio.open(src_files[0]) as dataset, MemoryFile() as memfile:
            # copy the dataset in the memoryfile using VRT driver
            riocopy(dataset, memfile.name, driver='VRT')
            # parse the content of the memoryfile into an xml tree
            vrt_xml = xml.etree.ElementTree.fromstring(memfile.read().decode('utf-8'))
            # add the SRS and GeoTransform subelements
            out_xml.append(vrt_xml.find("SRS"))
            out_xml.append(vrt_xml.find("GeoTransform"))
            logger.info(f"CRS and geotransorm from {src_files[0]} set as CRS and geotransform")
    # if value_unit is not None, add it to the output
    if value_unit is not None:
        if out_xml.find("Metadata") is None:
            SubElement(out_xml, "Metadata")
        if out_xml.find("Metadata").find("MDI[@key='VALUE_UNIT']") is None:
            SubElement(out_xml.find("Metadata"), "MDI", attrib={"key": "VALUE_UNIT"})
        out_xml.find("Metadata").find("MDI[@key='VALUE_UNIT']").text = str(value_unit)
        logger.info(f"{value_unit} set as unit name")
    # add each band to the VRT XML
    for band_number, (band, date) in enumerate(zip(out_bands, dates), start=1):
        # change the band number from the one of the src file to the one in the built vrt
        band.set("band", str(band_number))
        #  if date is not provided, check if the end of the description is a date
        if date is None and band.find("Description") is not None:
            try:
                description_date = band.find("Description").text[-8:]
                datetime.datetime.strptime(description_date, "%Y%m%d")
                date = description_date
            except ValueError:
                pass
        # if date is provided update/add the DATE tag
        if date is not None:
            if band.find("Metadata") is None:
                SubElement(band, "Metadata")
            if band.find("Metadata").find("MDI[@key='DATE']") is None:
                SubElement(band.find("Metadata"), "MDI", attrib={"key": "DATE"})
            band.find("Metadata").find("MDI[@key='DATE']").text = str(date)
        # if scale_factor then change the source from SimpleSource to ComplexSource with ScaleRatio
        if scale_factor is not None:
            complex_source = band.find("SimpleSource")
            complex_source.tag = "ComplexSource"
            if band.find("NoDataValue") is not None:
                SubElement(complex_source, "NODATA")
                complex_source.find("NODATA").text = band.find("NoDataValue").text
            SubElement(complex_source, "ScaleRatio")
            complex_source.find("ScaleRatio").text = str(scale_factor)
            SubElement(complex_source, "ScaleOffset")
            complex_source.find("ScaleOffset").text = str(0)
        out_xml.append(band)
    # indent the VRT XML
    indent(out_xml)
    # write the VRT XML in the out file
    ElementTree(out_xml).write(out_filename, encoding="utf-8")
    logger.info(f"VRT file {out_filename} of {sum(len(_) for _ in bands)} bands created.")
    return True
