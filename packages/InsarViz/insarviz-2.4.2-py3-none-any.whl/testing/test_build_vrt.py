# -*- coding: utf-8 -*-
"""
unit tests for insarviz.build_vrt
"""

import logging
import unittest
from pathlib import Path
import datetime

from insarviz.build_vrt import build_vrt
from insarviz.Loader import Loader

logger = logging.getLogger(__name__)


class Test_build_vrt(unittest.TestCase):

    def setUp(self):
        self.vrt_dir_path = f"{str(Path(__file__).resolve().parent)}/data/VRT_sources/"
        self.dates = [20190517, 20190529, 20190610, 20190622, 20190628, 20190704, 20190710,
                      20190716, 20190722, 20190728, 20190803, 20190809, 20190815, 20190827,
                      20190902, 20190908, 20190926]
        self.unit = "rad"

    def test_from_band_files_to_vrt(self):
        "Combine multiple bands each in a single file to a single VRT"
        src_files = list([f"{self.vrt_dir_path}band_{i}.tiff" for i in range(1, 18)])
        out = f"{self.vrt_dir_path}combined.vrt"
        build_vrt(src_files=src_files, bands=None, out_filename=out)
        logger.debug(f"built vrt in {out}")
        loader = Loader()
        loader.open(out)
        data = loader.dataset
        self.assertEqual(data.shape[0], 600)
        self.assertEqual(data.shape[1], 600)
        self.assertEqual(data.count, 17)
        self.assertEqual(data.nodata, 0.0)

    def test_tag_vrt(self):
        "Tag the vrt built in test_from_band_files_to_vrt"
        src_files = f"{self.vrt_dir_path}combined.vrt"
        out = f"{self.vrt_dir_path}tagged.vrt"
        build_vrt(src_files=src_files, bands=None, out_filename=out, dates=self.dates,
                  value_unit=self.unit)
        logger.debug(f"built vrt in {out}")
        loader = Loader()
        loader.open(out)
        data = loader.dataset
        self.assertEqual(data.shape[0], 600)
        self.assertEqual(data.shape[1], 600)
        self.assertEqual(data.count, 17)
        self.assertEqual(data.nodata, 0.0)
        self.assertEqual(loader.units, self.unit)
        self.assertIsInstance(loader.dates[0], datetime.datetime)

    def test_from_band_files_to_tag_vrt(self):
        "Combine multiple bands each in a single file to a single tagged VRT"
        src_files = list([f"{self.vrt_dir_path}band_{i}.tiff" for i in range(1, 18)])
        out = f"{self.vrt_dir_path}tagged_combined.vrt"
        build_vrt(src_files=src_files, bands=None, out_filename=out, dates=self.dates,
                  value_unit=self.unit)
        logger.debug(f"built vrt in {out}")
        loader = Loader()
        loader.open(out)
        data = loader.dataset
        self.assertEqual(data.shape[0], 600)
        self.assertEqual(data.shape[1], 600)
        self.assertEqual(data.count, 17)
        self.assertEqual(data.nodata, 0.0)
        self.assertEqual(loader.units, self.unit)
        self.assertIsInstance(loader.dates[0], datetime.datetime)
