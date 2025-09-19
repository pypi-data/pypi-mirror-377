=============
Release Notes
=============

2.4.2 (2025-09-18)
------------------

New
```

- Right-click "create temporary point" function
- View InsarViz logs within InsarViz

2.4.1 (2025-09-12)
------------------

New
```

- Right-click "lock axes" function

Changed
```````

- Automatically revert to interactive mode after creating a point or profile

Fixed
`````

- Handle NaNs as nodata when computing histograms

2.4.0 (2025-07-18)
------------------

New
```

- MapSwipe tool
- Right-click copy coordinates to clipboard
- Use the new 'rules' in our CI configuration

Fixed
`````

- histograms not computed correctly on certain datasets

2.3.0 (2025-01-29)
------------------

New
```

- OpenStreetMap layer
- a reference band can be chosen (i.e. subtracted to every other band)
- XYZ and WMTS layers
- csv exporter redone
- cyclic colormaps
- compute histograms in a separate process + cancel button
- harmonize path format in project between linux / mac / windows
- display project/cube path in title bar
- use pyside6 instead of pyqt5

Fixed
`````

- display bug on mac




2.2.1 (2024-11-12)
------------------

New
```

- compute histograms in a separate thread




2.2.0 (2024-11-08)
------------------

Fixed
`````

- use Qt binding of opengl to fix display issues on Linux + Wayland


2.1.0 (2024-09-13)
------------------

New
```

- projects (save your settings, points, profiles, references, layers)
- layers (raster one band, raster RGB, openstreetmap)
- points, profiles and references are customisable (name, color...)
- timeline when dates are available
- points and profiles customisable width
- histograms are now computed for each band and for whole dataset at the start and colormap settings are based on whole dataset
- dates and units are now in band and file tags
- standard deviation for spatial profiles
- undo / redo hotkeys (in Edit menu)
- icons representing points and references when zoomed out
- core opengl instead of fixed function pipeline

Fixed
`````

- reference performance
- non linear colormaps
- textures were loaded vertically flipped
- nodata is correctly displayed when zoomed out


1.0.4 (2023-03-13)
------------------

New
```

- new colour gradients (from Crameri et al., see Doc)
- Clear Reference button
- keyboard shortcuts + tooltips on profiling tools
- autorange histogram to 5/95th percentiles (button in toolbar and in context menu)
- Map toolbar with 2 buttons:
	* Flip Map Vertically feature
	* Save Map to export map view + assoc. colorbar to image files (multiple formats available) ('#75 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/issues/75>)

- Menu entry to save all figures to repository (multiple formats available) ('#75 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/issues/75>)
- support VRT (GDAL Virtual Format) loading ('#73 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/issues/73>) + VRT building script (see Doc)
- pypi packaging


Fixed
`````
- colour display bug on Linux/Windows (discretisation)
- reference display on Linux/Windows ('#70 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/issues/70>)
- plot ranges remain when clicking points
- jump to image 99 upon first loading, now remains on middle image
- handle nodata absent from header
- plot bug when switching between tools
- date slider/spinbox discrepancy
- colour palette also applied to general view


Changed
```````
- boundaries eased up on versions of required packages
- plot titles/descriptions outside of figures
- plot background icon
- Reference now only through Reference tool (no check button in plot window anymore)
- geotiff not flipped automatically upon loading
- LOS symbol disabled for now, needs rethinking
- Documentation updated


1.0.3 (2022-09-16)
------------------

New
```

- Profile tool now links two points selected by the user, and draws plots for a selection of points (regular spacing) on this profile line (`!55 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/merge_requests/55>`_)
- Points tool now allows user to select individual points whose data are to be plotted (`!55 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/merge_requests/55>`_)
- Reference tool: once data is plotted from Profile or Points tool, a reference point or zone (rectangle) can be selected on the Map by the user, plots will be adjusted to the reference (`!55 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/merge_requests/55>`_)


Fixed
`````
- lock axes button on plots did not work on Linux (`#56 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/issues/56>`_)
- export to csv was faulty when more than one curve on plot ('#66 <https://gricad-gitlab.univ-grenoble-alpes.fr/deformvis/insarviz/-/issues/66>)


Changed
```````
- Profile tool renamed Points (see New section)
- Documentation updated
