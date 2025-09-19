#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loader

This module manages data loading from a file.
Contains the class:
    * Loader
and its methods:
    * open - open data file and store dataset
    * __len__ - length of dataset (# of bands or dates)
    * _dates - list of dates or list of band #
    * load_band - load one band data (all points) from file
    * load_profile - load one point data (all dates) from file
    * get_metadata - get metadata from file if exists
"""

from typing import Optional, Union

import logging
import traceback

import time

import pathlib

import multiprocessing

import datetime

import warnings

import asyncio

from qasync import asyncSlot

import concurrent.futures

import numpy as np

import rasterio
import rasterio.warp

from PySide6.QtCore import QObject, Signal, Slot

from insarviz.utils import normalize_path

logger = logging.getLogger(__name__)


# data ######################################################################


class Loader(QObject):

    # used to find the outliers: values outside
    # [q25 - outlier_threshold*IQR, q75 + outlier_threshold*IQR]
    outlier_threshold = 4  # classicaly 1.5, but a higher value seems nicer

    # emited when a dataset is opened, pass the starting band index
    data_loaded = Signal(int)
    data_units_loaded = Signal(str)
    histograms_computed = Signal()
    computing_histograms = Signal()
    data_invalidated = Signal()
    reference_band_index_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.filepath: Optional[pathlib.Path] = None
        self.dataset: Optional[rasterio.DatasetReader] = None
        self.reference_band_index: Optional[int] = None
        self.reference_band: Optional[np.ndarray] = None
        self.metadata: dict[str, str] = {}
        self.dates: Union[list[datetime.datetime], list[int]] = []
        self.timestamps: Optional[np.ndarray] = None  # array of floats representing self.dates
        self.units: str = ""
        self.total_histogram: Optional[tuple[np.ndarray, np.ndarray]] = None
        self.band_histograms: list[tuple[np.ndarray, np.ndarray]] = []
        self.process_manager = multiprocessing.Manager()
        self.cancel_compute_histograms_event: Optional[multiprocessing.Event] = None
        self.compute_histograms_task: Optional[asyncio.Future] = None
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=1)

    def open(self, filepath: pathlib.Path) -> None:
        """
        Open data file and store dataset.

        Parameters
        ----------
        filepath : str, path
            Name of the file to load (with path).
        """
        self.filepath = normalize_path(filepath)
        with warnings.catch_warnings():
            # ignore RuntimeWarning for slices that contain only nans
            warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning,
                                    message="Dataset has no geotransform, gcps, or rpcs. The identity matrix will be returned.")
            self.dataset = rasterio.open(self.filepath)
        logger.info(f"opened {self.filepath}")
        profile = self.dataset.profile
        logger.info("Dataset profile:\n" +
                    "\n".join([f"\t{attr} {profile[attr]}" for attr in profile]))
        self.get_metadata(self.filepath)
        # value units
        try:
            self.units = self.dataset.tags()['VALUE_UNIT']
            logger.info(f'Value unit "{self.units}" found in dataset VALUE_UNIT tag')
        except KeyError:
            logger.info(f"{self.filepath} missing VALUE_UNIT dataset tag")
            try:
                #  TODO ugly fix because flatsim has problems in its metadata
                self.units = self.metadata['Value_unit'].split(",")[0]
                logger.info(f'value unit "{self.units}" found in .meta file')
            except KeyError:
                self.units = 'Undefined units'
                logger.warn(f'no value unit found, taking "{self.units}" instead')
        self.data_units_loaded.emit(self.units)
        # dates and timestamps
        try:
            self.dates = [datetime.datetime.strptime(str(self.dataset.tags(i)["DATE"]), "%Y%m%d")
                          for i in self.dataset.indexes]
            self.timestamps = np.array([d.timestamp() for d in self.dates], dtype=float)
            logger.info("dates found in DATE band tags")
        except (KeyError, ValueError) as error:
            if isinstance(error, KeyError):
                logger.warn(f"{self.filepath} missing DATE band tags")
            if isinstance(error, ValueError):
                logger.info(f"{self.filepath} DATE band tags are not well formated (%Y%m%d expected"
                            ' as for example "20240827", see '
                            'https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)')
            try:
                self.dates = [datetime.datetime.strptime(x[-8:], "%Y%m%d")
                              for x in self.dataset.descriptions]
                self.timestamps = np.array([d.timestamp() for d in self.dates], dtype=float)
                logger.info("dates found in band descriptions (last 8 characters)")
            except (ValueError, TypeError):
                logger.warn("no date found, taking band numbers as indexes instead")
                self.dates = self.dataset.indexes
                self.timestamps = np.array(self.dates, dtype=float)
        self.total_histogram = (np.array([]), np.array([]))
        self.band_histograms = [(np.array([]), np.array([])) for i in range(len(self))]
        logger.info(f"number of bands = {len(self)}")
        self.data_loaded.emit(self.dataset.indexes[len(self)//2])

    def close(self) -> None:
        if self.dataset is not None:
            self.cancel_compute_histograms()
            logger.info(f"closing {self.filepath}")
            self.dataset.close()
        self.dataset = None
        self.filepath = None
        self.reference_band_index = None
        self.reference_band = None
        self.metadata = {}
        self.dates = []
        self.timestamps = None
        self.units = ""
        self.total_histogram = None
        self.band_histograms = []

    def __len__(self) -> int:
        """
        Length of dataset = number of bands/dates.

        Returns
        -------
        int
            number of band/dates.
        """
        assert self.dataset is not None, "Loader.len: no dataset opened"
        return len(self.dataset.indexes)

    @asyncSlot(tuple)
    async def compute_histograms(self, binrange: Optional[tuple[float, float]] = None) -> None:
        """
        _summary_

        Parameters
        ----------
        bands : Optional[Union[int], list[int]], optional
            Indexes of dataset bands to sample, by default None meaning all bands.
        """
        assert self.dataset is not None, "Loader.compute_histogram: no dataset opened"
        assert self.filepath is not None
        self.computing_histograms.emit()
        self.cancel_compute_histograms_event = self.process_manager.Event()
        loop = asyncio.get_running_loop()
        self.compute_histograms_task = loop.run_in_executor(self.process_pool,
                                                            compute_histograms_worker,
                                                            *(self.filepath,
                                                              self.cancel_compute_histograms_event,
                                                              binrange))
        try:
            await self.compute_histograms_task
        except Exception as e:
            logger.error(traceback.format_exc())

        self.cancel_compute_histograms_event = None
        if not self.compute_histograms_task.cancelled():
            self.set_histograms(*self.compute_histograms_task.result())
        else:
            self.set_histograms(self.total_histogram, self.band_histograms)
        self.compute_histograms_task = None

    def cancel_compute_histograms(self):
        if self.total_histogram is None or len(self.total_histogram) == 0:
            return
        if self.compute_histograms_task is not None:
            self.compute_histograms_task.cancel()
            if self.cancel_compute_histograms_event is not None:
                self.cancel_compute_histograms_event.set()

    def set_histograms(self, total_histogram: tuple[np.ndarray, np.ndarray],
                       band_histograms: list[tuple[np.ndarray, np.ndarray]]) -> bool:
        assert self.dataset is not None
        if len(band_histograms) != len(self):
            logger.warning("number of band histograms not equal to number of bands")
            return False
        total_histogram = tuple([np.array(a) for a in total_histogram])
        if len(total_histogram[0].shape) != 1 or len(total_histogram[1].shape) != 1:
            logger.warning("total histogram is not an array of dimension 1")
            return False
        if len(total_histogram[1]) != len(total_histogram[0]) + 1:
            logger.warning("total histogram number of bins is not equal to number of values + 1")
            return False
        for i in range(len(self)):
            band_histograms[i] = tuple([np.array(a) for a in band_histograms[i]])
            if len(band_histograms[i][0].shape) != 1 or len(band_histograms[i][1].shape) != 1:
                logger.warning(f"band {self.dataset.indexes[i]} histogram is not an array of "
                               "dimension 1")
                return False
            if len(band_histograms[i][1]) != len(band_histograms[i][0]) + 1:
                logger.warning(
                    f"band {self.dataset.indexes[i]} histogram number of bins is not equal to "
                    "number of values + 1")
                return False
        self.total_histogram = total_histogram
        self.band_histograms = band_histograms
        self.histograms_computed.emit()
        return True

    def load_band(self, i: int, use_reference: bool = True) -> np.ndarray:
        """
        load band i from dataset

        Parameters
        ----------
        i : int, optional
            Band number to load. The default is 0.

        Returns
        -------
        band : array
            Loaded band data.
        """
        assert self.dataset is not None, "Loader.load_band: no dataset opened"
        assert i in self.dataset.indexes
        t0 = time.time()
        band = self.dataset.read(i)
        try:
            no_data = self.dataset.nodatavals[i]
        except (IndexError, AttributeError):
            try:
                no_data = self.dataset.nodata
            except AttributeError:
                no_data = np.nan
        if no_data is not np.nan:
            band[band == no_data] = np.nan
        if use_reference:
            if self.reference_band_index is not None and self.reference_band is not None:
                band = band - self.reference_band
        t1 = time.time()
        logger.info(f"loaded band {i} in {t1-t0} s")
        return band

    def load_profile_window(self, i_start: float, j_start: float, i_stop: Optional[float] = None,
                            j_stop: Optional[float] = None) -> np.ndarray:
        assert self.dataset is not None, "Loader.load_profile_window: no dataset opened"
        i, j = int(i_start), int(j_start)
        width = abs(i_start - int(i_stop)) + 1 if i_stop else 1
        length = abs(j_start - int(j_stop)) + 1 if j_stop else 1
        data = self.dataset.read(self.dataset.indexes,
                                 window=rasterio.windows.Window(i, j, width, length))
        for index in range(len(self)):
            try:
                no_data = self.dataset.nodatavals[self.dataset.indexes[index]]
            except (IndexError, AttributeError):
                try:
                    no_data = self.dataset.nodata
                except AttributeError:
                    continue
            data[index][data[index] == no_data] = np.nan
        if self.reference_band_index is not None and self.reference_band is not None:
            data = data - self.reference_band[j:j+length, i:i+width]
        with warnings.catch_warnings():
            # ignore RuntimeWarning for slices that contain only nans
            warnings.filterwarnings("ignore", category=RuntimeWarning,
                                    message="Mean of empty slice")
            data = np.nanmean(data, axis=(1, 2))
        return data

    @Slot(object)
    def set_reference_band(self, index: Optional[int]) -> None:
        if index is not None:
            index = int(index)
        if self.reference_band_index != index:
            self.reference_band_index = index
            if self.reference_band_index is None:
                self.reference_band = None
            else:
                self.reference_band = self.load_band(self.reference_band_index, use_reference=False)
            logger.info(f"reference band changed: {self.reference_band_index}")
            self.data_invalidated.emit()
            self.reference_band_index_changed.emit(self.reference_band_index)

    def get_metadata(self, filename: pathlib.Path) -> None:
        """
        Create a dictionnary containing all metadata entries in self.matadata,
        if a '.meta' file exists in same repo as the datacube file

        Parameters
        ----------
        filename : pathlib.Path
            name of the datacube file
        """
        metafilename = filename.with_suffix('.meta')
        self.metadata = {}
        try:
            with open(metafilename, encoding="utf-8") as f:
                for line in f:
                    try:
                        (key, val) = line.split(sep=': ', maxsplit=1)
                        self.metadata[key] = val.strip()
                    except ValueError:
                        pass
        except FileNotFoundError:
            logger.info("no metadata file found")


# COMPUTE HISTOGRAMS WORKER FUNCTION ###############################################################
def compute_histograms_worker(filepath: pathlib.Path, stop_event: multiprocessing.Event,
                              binrange: Optional[tuple[float, float]] = None):
    dataset = rasterio.open(filepath)
    # intialize progress dialog
    t0 = time.time()
    # xy is an array of (row, col, band) positions to randomly sample the dataset
    sample_size = 20000
    xy = np.random.randint([dataset.height, dataset.width, len(dataset.indexes)],
                           size=(sample_size, 3))

    # sort xy to optimize dataset sampling (split between interleaving cases)
    if len(set(dataset.block_shapes)) == 1:
        # block shape is the same across bands
        block_height, block_width = dataset.block_shapes[0]
        if dataset.interleaving == rasterio.enums.Interleaving.pixel:
            # sort xy first by block row, second by block column
            xy = xy[np.lexsort((xy[:, 1] // block_width, xy[:, 0] // block_height))]
        elif (dataset.interleaving == rasterio.enums.Interleaving.band
                or (dataset.driver == 'VRT' and dataset.interleaving is None)):
            # sort xy first by band, second by block row, third by block column
            xy = xy[np.lexsort(
                (xy[:, 1] // block_width, xy[:, 0] // block_height, xy[:, 2]))]
        else:
            raise NotImplementedError(
                f"interleaving:{dataset.interleaving} not implemented")
    else:
        # block shape is not the same across bands so interleaving must be band
        assert dataset.interleaving == rasterio.enums.Interleaving.band
        # sort xy by band
        xy = xy[np.lexsort((xy[:, 2]))]
    if stop_event.is_set():
        raise asyncio.CancelledError
    # sample the dataset
    sample = np.empty(sample_size)
    for i in range(20):
        # split in 20 steps to update the progress dialog
        start = (i * sample_size) // 20
        stop = ((i+1) * sample_size) // 20
        sample[start:stop] = np.array([
            dataset.read(dataset.indexes[k[2]],
                         window=rasterio.windows.Window(k[1], k[0], 1, 1))[0][0]
            for k in xy[start:stop]])
        if stop_event.is_set():
            raise asyncio.CancelledError
    if dataset.nodata is not None:
        if np.isnan(dataset.nodata):
            sample = sample[~np.isnan(sample)]
        else:
            sample = sample[sample != dataset.nodata]
    IQR = 0.0
    percentileBounds = (25,75)
    while IQR == 0.0:
        # compute the histogram bins on the sample
        # get the first and third quartiles (inverted_cdf means exact observation)
        qMin, qMax = np.percentile(sample, percentileBounds, method="inverted_cdf")
        percentileBounds = (percentileBounds[0]*0.5, 50+percentileBounds[1]*0.5)
        # interquartile range
        IQR = qMax - qMin
    # Freedman Diaconis Estimator of the binwidth
    binwidth = 2 * IQR / (np.cbrt(len(sample)))
    if binrange is None:
        # range exclude outliers, ie observations outside of
        # [q25 - outlier_threshold*IQR, q75 + outlier_threshold*IQR]
        binrange = (qMin - Loader.outlier_threshold*IQR,
                    qMax + Loader.outlier_threshold*IQR)
    # compute the bin count as in np.histogram_bin_edges
    bincount = int(np.round(np.ceil((binrange[1] - binrange[0]) / binwidth)))
    # compute the bins
    bins = np.histogram_bin_edges(sample, bins=bincount, range=binrange)
    # add a bin at the start and end for outliers
    bins_total = np.array([bins[0], *bins, bins[-1]])
    bins_band = [np.array([bins[0], *bins, bins[-1]]) for _ in range(len(dataset.indexes))]
    if stop_event.is_set():
        raise asyncio.CancelledError
    # build the histograms (split between interleaving cases)
    nd = dataset.profile['nodata']
    histogram_total = np.zeros(bins_total.shape[0]-1)
    histograms_band = [np.zeros(bins_band[i].shape[0]-1)
                       for i in range(len(dataset.indexes))]
    with warnings.catch_warnings():
        # ignore RuntimeWarning for slices that contain only nans
        warnings.filterwarnings("ignore", category=RuntimeWarning,
                                message="All-NaN slice encountered")
        if dataset.interleaving == rasterio.enums.Interleaving.pixel:
            # pixel interleaving => open block by block
            assert len(set(dataset.block_shapes)) == 1
            block = np.empty((len(dataset.indexes), *dataset.block_shapes[0]))
            block_count = sum(1 for _ in dataset.block_windows())
            for k, window in enumerate(dataset.block_windows()):
                block = dataset.read(window=window[1], out=block)
                block[block == nd] = np.nan
                for i in range(len(dataset.indexes)):
                    tmp_min = np.nanmin(block[i])
                    bins_total[0] = np.nanmin((tmp_min, bins_total[0]))
                    bins_band[i][0] = np.nanmin((tmp_min, bins_band[i][0]))
                    tmp_max = np.nanmax(block[i])
                    bins_total[-1] = np.nanmax((tmp_max, bins_total[-1]))
                    bins_band[i][-1] = np.nanmax((tmp_max, bins_band[i][-1]))
                    tmp_hist = np.histogram(block[i], bins=bins_band[i])[0]
                    histograms_band[i] += tmp_hist
                    histogram_total += tmp_hist
                if stop_event.is_set():
                    raise asyncio.CancelledError
        else:
            # band interleaving or no interleaving metadata => open band by band
            band = np.empty(dataset.shape)
            band_count = len(dataset.indexes)
            for i, idx in enumerate(dataset.indexes):
                band = dataset.read(idx, out=band)
                band[band == nd] = np.nan
                band_min = np.nanmin(band)
                bins_total[0] = np.nanmin((band_min, bins_total[0]))
                bins_band[i][0] = np.nanmin((band_min, bins_band[i][0]))
                band_max = np.nanmax(band)
                bins_total[-1] = np.nanmax((band_max, bins_total[-1]))
                bins_band[i][-1] = np.nanmax((band_max, bins_band[i][-1]))
                histograms_band[i] += np.histogram(band, bins=bins_band[i])[0]
                histogram_total += histograms_band[i]
                if stop_event.is_set():
                    raise asyncio.CancelledError
    # normalize the histograms in order to plot them in ColormapWidget
    for i, h in enumerate(histograms_band):
        histograms_band[i] = h / sum(h)
    histogram_total = histogram_total / sum(histogram_total)
    t1 = time.time()
    logger.info(f"computed histograms in {t1-t0}s ({len(bins)-1} bins)")
    if stop_event.is_set():
        raise asyncio.CancelledError
    return (histogram_total, bins_total), list(zip(histograms_band, bins_band))
