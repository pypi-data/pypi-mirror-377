Supported data formats
======================

Supported input formats include datacubes in the `GDAL <https://gdal.org/index.html>`_-supported formats, such as:

* Tiff and GeoTiff
* NSBAS-type time series (depl_cumule and associated files)
* VRT (Virtual Datasets): this GDAL format is a virtual dataset composed of other GDAL datasets with repositioning and algorithms potentially applied, as well as various kinds of metadata altered or added (see `documentation <https://gdal.org/drivers/raster/vrt.html>`_).
  For instance, you can make a VRT composed of individual displacement map files or interferograms.


Create a VRT using insarviz.build_vrt
-------------------------------------

We provide inside InsarViz a Python function to create a VRT.

.. autofunction:: insarviz.build_vrt.build_vrt

You can use it by opening a Python console (inside the environment in which you installed InsarViz):

.. code-block :: bash
 
 python3

And then import ``insarviz.build_vrt.build_vrt`` and use the function:

.. code-block :: python

  from insarviz.build_vrt import build_vrt
  
  scr_files = ["file_1.tiff", "file_2.tiff"]
  bands = [[1,3], [2]]
  dates = [20200518, 20200620, 20200722]
  build_vrt(scr_files=scr_files, bands=bands, out_filename="out.vrt", dates=dates, value_unit="rad")

The previous code build a VRT ``out.vrt`` where:

* The first band is the first band of ``file_1.tiff`` dated as 18th May 2020
* The second band is the third band of ``file_1.tiff`` dated as 20th June 2020
* The third band is the second band of ``file_2.tiff`` dated as 22th July 2020
* The value unit is defined as "rad"

The function ``insarviz.build_vrt.build_vrt`` returns ``True`` if the VRT was created successfully, and ``False`` if a problem happened.