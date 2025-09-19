########
Tutorial
########

Install InsarViz
----------------
To install the InsarViz tool, please follow the `installation instructions <https://deformvis.gricad-pages.univ-grenoble-alpes.fr/insarviz/installation.html>`_.

Launch InsarViz
---------------

Once InsarViz is correctly installed, first make sure that you are in the virtual environment used during installation, and then simply use the command:

.. code-block :: bash

        ts_viz

If you want to launch the tool directly with a data file or an insarviz project opened, then use the `-i` option:

.. code-block :: bash

        ts_viz -i /path/to/my/data_or_project_file

Main window
-----------

The main window that opens up when you launch the tool is divided into three vertical columns:

* On the left, from top to bottom, you will find the **Layer panel** and the **Minimap** sub-window.
* In the center, the **Band slider** and the main **Map**.
* On the right, the **Colormap panel**.

.. image:: images/interface_overview.png
  :width: 1920
  :alt: interface overview image

* The **Layer panel** shows the layers, their order and their properties.
* The **Minimap** is a full-extent view of the map with a white rectangle marking the area currently displayed in the **Map**, only the *Main Data Layer* is displayed. It can be detached from the main window or closed. Check the menu **View > Minimap** to show it again after you have closed it.
* The **Band slider** allows you to navigate in the temporal dimension of the dataset, either by setting a band number directly or using the slider to navigate between bands. When available in metadata, the dates corresponding to the bands are shown on an interactive timeline under the band slider.
* The **Map** is where the current layers are displayed.
* The **Colormap panel** is where you control the colormap for the main data layer.

Load data
---------
You can load data using the menu **File > Open datacube or project** (see `Supported formats <https://deformvis.gricad-pages.univ-grenoble-alpes.fr/insarviz/supported.html>`_).

When a dataset is loaded for the first time, the histogram of every band is computed.
This can take some time (up to a few minutes on a large dataset).
If you save your work inside an *InsarViz project* using the menu **File > Save project**, the histograms are saved within the project and thus won't be recomputed again when you reopen it.
Loading time is shown in the Terminal.

**Note on performance:** the dataset is loaded dynamically, as you navigate through the bands, new bands are loaded and rendered.
Only the rendering image is stored for later display, the data itself is not stored as this would dramatically reduce performance.


Colormap
--------

The **Colormap panel** is used to control the color rendering of the *Main Data Layer* in the **Map** and the **Minimap**.

On the left, the histograms show the distribution of the data values.
The blue histogram represents *all the bands* (the whole dataset), while the red histogram represents the *current band*.
Histograms can be hidden by **left-clicking** on their color in the bottom legend.
You can **scroll** or **right-click + drag** to *zoom in/out* on the histograms.

The colorbar on the right shows the current *colormap*, which can be changed through **right-click**.

The area in blue on the histograms shows the *mapping of the colormap on the data distribution*.
You can move this area and change its boundaries using **left-click + drag**.

.. video:: images/colormap.mp4
  :alt: colormap video
  :poster: images/colormap_thumbnail.jpg
  :autoplay:
  :loop:
  :preload: auto
  :width: 960

|

On the top of the **Colormap panel** are three buttons:

* **Autorange all bands** change the mapping of the colormap to cover the *range between the 2th percentile and the 98th percentile* of all bands (the whole dataset).
* **Autorange current band** change the mapping of the colormap to cover the *range between the 2th percentile and the 98th percentile* of the current band.
* **Recompute histograms** recompute the histogram taking the values outside of the area in blue as outliers.

For example, if a lot of values are in the most extreme bins of the histograms after their initial computation, you can compute them again by extending the area in blue and clicking on **Recompute histograms**.

.. video:: images/recompute_histograms.mp4
  :alt: recompute histograms video
  :poster: images/recompute_histograms_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

Navigate through space and time
-------------------------------

In the **Map** and **Minimap**, you can:

* **Left-click + drag** to *move spatially around*.
* **Scroll** to *zoom in/out*.

To navigate in the *temporal dimension*, use the **Band Slider** at the top of the **Map**.
When available in the file metadata, (see `Supported formats <https://deformvis.gricad-pages.univ-grenoble-alpes.fr/insarviz/supported.html>`_), an *interactive timeline* is also displayed.
This timeline can be *zoomed in/out* using **right-click + drag** or **scroll**.
You can also sepcify a *reference band* that will be substracted to every other band.

When you hover over the **Map**, information on the point currently under the mouse cursor (coordinates and value) are displayed in the **footer** of the window and in the **cursor tooltip**.

*Nodata* or *NaN* points are not rendered, they appear in the same dark grey as the background.

.. video:: images/map_navigation.mp4
  :alt: map navigation video
  :poster: images/map_navigation_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

You can *flip* the **Map** vertically or horizontally using the menu **View > Flip Vertically** or **View > Flip Horizontally**.

.. video:: images/flip.mp4
  :alt: flip video
  :poster: images/flip_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

Plot curves
-----------

Plot windows
############

Select the menu **View > Plotting** to dislay the plotting windows (or **Ctrl+P**).
This opens two new tabbed windows on the right of the main window: the **Temporal Profile** window and the **Spatial Profile** window.
Those windows can be *detached* from the main window or closed.
Check the menu **View > Plotting** again to show them back after you have closed them.

* In the **Temporal Profile** window, plots are *displacement versus time*.
  The *thick vertical line* in the **Temporal Profile** window marks the band/date currently displayed, and can be used to *change* the *current band/date* (**left-click + drag**).
* In the **Spatial Profile** window, plots are *displacement versus distance on the Map*.

.. video:: images/plot_windows.mp4
  :alt: plot windows video
  :poster: images/plot_windows_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

The *default tool* is **Interactive**.
This means that as you hover the cursor over the **Map**, a temporal profile of the point under the cursor is interactively drawn in the **Temporal Profile** window (thick red line).
This mode enables rapid, dynamic exploration of the whole dataset.

.. video:: images/pointer_curve.mp4
  :alt: pointer curve video
  :poster: images/pointer_curve_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

Selection tools
###############

There are three other tools that allow to define shapes and computes their temporal profiles:

* With the **Point** tool, you can define a square shape and display the temporal profile of its spatial mean in the **Temporal Profile** window.
  A **Point** has a *radius* (i.e. half of its width / height) that can be modified in the **Layer Panel**, its *name* and *color* can also be modified there (**double-left-click** on the field you want to modify).
.. video:: images/point.mp4
  :alt: point video
  :poster: images/point_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

* With the **Profile** tool, you can draw a *line* (or a *broken line*): the first **left-click** creates the starting point and subsequent **left-clicks** will extend the **Profile** line until you **right-click**.
  The temporal profile of each point along the line (or the temporal profile of the mean of each point's surface if the **Profile** has a radius > 1) can be displayed in the **Temporal Profile** window, a clock icon will be displayed on the map to show which point of the line is being displayed in the **Temporal Window**.
  Likewise, the spatial profile of the **Profile** can be displayed in the **Spatial Profile** window, a secondary **Band Slider** in the **Spatial Profile** window enables you to navigate through time there, a map icon will be displayed on the map to represent the *interactive thick vertical line*.
  A **Profile** has a *radius*, just like a **Point**, that can be modified in the **Layer Panel**, its *name* and *color* can also be modified there.
  When a **Profile** has a radius > 1, each point of the line is like a **Point** with the same radius, thus the value of this point is the spatial mean of the square centered on this point with the same radius.
.. video:: images/profile.mp4
  :alt: profile video
  :poster: images/profile_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

* With the **Reference** tool, you can define a rectangular shape and  display the temporal profile of its spatial mean in the **Temporal Profile** window.
  The main use of a **Reference** is to adjust the plot of other **Points** or **Profile**: to substract the mean of the **Reference** to their curves.
  You can choose a **Reference** in either the **Temporal Profile** window or the **Spatial Profile** window to adjust all their displayed curves.
  A **Reference** name and color can be modified in the **Layer Panel**.
.. video:: images/reference.mp4
  :alt: reference video
  :poster: images/reference_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

Note that you can also switch between tools directly on the **Map** by performing a **right-click** that opens a menu enabling to create a new **Point**, **Profile** or **Reference**.

Plot options
############

* The plots are *zoomable* with **scroll or right-click+drag**.
  To go back to the full view, you can click the **Autorange button** on the top of the window, or **right-click > View all**.
  You can also adjust each axis limits manually by **left-click + dragging** or **scroll** on it, or **right-click > X-Axis / Y-Axis**.
  Once you are satisfied with the axes settings, you can lock them using the **Lock axes** checkable box on the top of the window.
  You can also show/hide *grids* and access other axes options (*log, invert*...) through **right-click > Plot Options**.
* To export the plot click the **Export...** button or use **right-click > Export**.
* The *color theme* of the plots can be changed (white or black background) using the **light/dark switch button** on the top of the window.

Add layers
----------

Select the menu **Layer > New ...** to add a new Layer.
For now, there are three types of layers you can add in InsarViz:

* If your data are *georeferenced*, you can add a *OpenStreetMap map* by selecting **Layer > New OpenStreetMap Layer**.
* If your data are *georeferenced*, you can add a *WMTS (Web Map Tile Service)* by selecting **Layer > New WMTS Layer** and filling in the required informations.
* If your data are *georeferenced*, you can add an *XYZ map server* by selecting **Layer > New XYZ Layer** and filling in the required informations (`see xyzservices doc <https://xyzservices.readthedocs.io/en/stable/index.html>`_).
* If you select **Layer > New Raster1B**, you can add a *single band* of a *raster file*.
  If your data are georeferenced, any georeferenced raster file can be added.
  If your data are not georeferenced, the added raster file *must* have the same shape as your data.
  You can also use another band of the raster file as a *mask*: any pixel where ``mask = 0`` will be discarded.
  You can change the *colormap* of this in the **Layer panel**.
* If you select **Layer > New RasterRGB**, you can add *three bands* of a *raster file* as an *RGB image*.
  If your data are georeferenced, any georeferenced raster file can be added.
  If your data are not georeferenced, the added raster file *must* have the same shape as your data.
  You can also use another band of the raster file as a *mask*: any pixel where ``mask = 0`` will be discarded.

.. video:: images/layers.mp4
  :alt: reference video
  :poster: images/layers_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960

|

A layer can be *hidden* by clicking on its checkbox in the **Layer panel**.
A layer as an *alpha* (*transparency*) value between 1 and 0, that can be changed in the **Layer panel**.
Layers *order* can be changed by **dragging** them up above or below one another.

swipe tools
#############

As of InsarViz 2.3.1, you can add "swipe tools". A swipe tool
doesn't contain any data, but instead allows you to hide part of the
layers above it to reveal underlying information.

You can adjust the cutoff point of the swipe tool by sliding left or
right, as shown below.

.. video:: images/swipe-tool.mp4
  :alt: reference video
  :poster: images/swipe-tool_thumbnail.jpg
  :loop:
  :preload: auto
  :width: 960
