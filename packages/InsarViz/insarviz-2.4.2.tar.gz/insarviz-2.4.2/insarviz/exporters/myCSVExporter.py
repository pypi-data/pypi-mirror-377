#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" myCSVExporter

This module contains a custom class myCSVExporter that manages the format
of data export from plots to CSV file.
Contains class:
    * myCSVExporter - export plot data to custom csv file
and method:
    * dt_to_dec - convert a datetime to decimal year
"""

import logging
import datetime
import csv
import itertools


import pyqtgraph as pg

import insarviz.plot.TemporalPlotView
import insarviz.plot.SpatialPlotView

logger = logging.getLogger(__name__)


class myCSVExporter(pg.exporters.CSVExporter):
    Name = "CSV"

    def parameters(self):
        return None

    def export(self, fileName=None):
        if not isinstance(self.item, pg.PlotItem):
            raise TypeError("Must have a PlotItem selected for CSV export.")
        if fileName is None:
            self.fileSaveDialog(filter="*.csv")
            return None
        try:
            self.item.insarviz_widget
        except AttributeError:
            return super().export(fileName)
        if isinstance(self.item.insarviz_widget, insarviz.plot.TemporalPlotView.TemporalPlotWidget):
            return self.temporal_plot_export(fileName)
        if isinstance(self.item.insarviz_widget, insarviz.plot.SpatialPlotView.SpatialPlotWidget):
            return self.spatial_plot_export(fileName)
        return super().export(fileName)

    def temporal_plot_export(self, fileName):
        header = []
        data_columns = []
        unit = str(self.item.insarviz_widget.plot_model.loader.units)
        header.append("Band")
        data_columns.append(self.item.insarviz_widget.plot_model.loader.dataset.indexes)
        if isinstance(self.item.getAxis("bottom"), pg.DateAxisItem):
            dates = self.item.insarviz_widget.plot_model.loader.dates
            header.append("Date (YYYY-MM-DD)")
            data_columns.append([d.strftime("%Y-%m-%d") for d in dates])
            header.append("Date (decimal year)")
            data_columns.append([dt_to_dec(d) for d in dates])
        for k, item in enumerate(self.item.items):
            if hasattr(item, 'implements') and item.implements('plotData'):
                if hasattr(item, 'getOriginalDataset'):
                    # try to access unmapped, unprocessed data
                    item_data = item.getOriginalDataset()
                else:
                    # fall back to earlier access method
                    item_data = item.getData()
                if item_data[0] is None:
                    # no data found, break out...
                    continue
                if len(item_data[0]) != len(data_columns[0]):
                    raise RuntimeError("curve has a number of point unequal to the number of bands")
                data_columns.append(item_data[1])
                if item.name() is not None:
                    header.append(str(item.name()).replace('"', '""') + " (" + unit + ")")
                else:
                    header.append(f"curve {k}")
        with open(fileName, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            for row in itertools.zip_longest(*data_columns, fillvalue=""):
                writer.writerow(row)

    def spatial_plot_export(self, fileName):
        header = []
        data_columns = []
        profile_curve_found = False
        unit = str(self.item.insarviz_widget.plot_model.loader.units)
        for item in self.item.items:
            if hasattr(item, 'implements') and item.implements('plotData'):
                if not profile_curve_found:
                    profile_curve_found = True
                    if hasattr(item, 'getOriginalDataset'):
                        # try to access unmapped, unprocessed data
                        item_data = item.getOriginalDataset()
                    else:
                        # fall back to earlier access method
                        item_data = item.getData()
                    if item_data[0] is None:
                        # no data found, break out...
                        logger.warning("CSV exporter: Empty profile curve")
                        item_data = [[], []]
                    bottom_axis = self.item.getAxis("bottom")
                    header.append(
                        f"{bottom_axis.labelText} ({bottom_axis.labelUnits})")
                    data_columns.append(item_data[0])
                    header.append(str(item.name()).replace('"', '""') + " (" + unit + ")")
                    data_columns.append(item_data[1])
                else:
                    raise RuntimeError("two curves")
        with open(fileName, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            for row in itertools.zip_longest(*data_columns, fillvalue=""):
                writer.writerow(row)


def dt_to_dec(dt):
    """Convert a datetime to decimal year. Time is at beginning of day.
    from https://stackoverflow.com/questions/29851357/python-datetime-to-decimal-year-one-day-off-where-is-the-bug"""
    year_start = datetime.datetime(dt.year, 1, 1)
    year_end = year_start.replace(year=dt.year+1)
    return dt.year + ((dt - year_start).total_seconds() /  # seconds so far
                      float((year_end - year_start).total_seconds()))  # seconds in year
