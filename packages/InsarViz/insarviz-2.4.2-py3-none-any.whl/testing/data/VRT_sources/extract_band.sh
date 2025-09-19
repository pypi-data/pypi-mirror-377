#!/bin/bash

for i in {1..17}
do
    gdal_translate ../GDM_DTs_geo_20190517_20190926_8rlks_crop_cmp.tiff band_$i.tiff -b $i
done

