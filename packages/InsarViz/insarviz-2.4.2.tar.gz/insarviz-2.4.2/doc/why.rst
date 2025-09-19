Why InsarViz?
*************

Insarviz is a tool designed to visualize and interactively
explore the spatiotemporal datacubes derived from the InSAR data processing chain.


Satellite Synthetic Aperture Radar (SAR) Interferometry (InSAR) is a 
well-established technique in Earth Observation (EO) that enables very high 
precision monitoring of ground displacements (mm/year). This method combines 
high spatial resolution data (up to a few meters) and large coverage capabilities 
(up to continental scale) with a fairly high temporal resolution (a few days 
to a few weeks). It is used to study a wide range of phenomena that impact the Earth 
surface (e.g. earthquakes, landslides, permafrost evolution, volcanoes, glaciers 
dynamics, subsidence, building and infrastructure deformation, etc.). 

For several reasons (data availability, non-intuitive radar image geometry, 
complexity of the processing, etc.), InSAR has long remained a niche technology 
and few free open-source tools have been dedicated to it compared to the widely-used, 
multi-purpose optical imagery. Most existing tools are focused on data processing.
Generic remote-sensing or Geographic Information System (GIS) softwares are limited when 
used to visualize InSAR data, due to their unusual geometry and formats. A few 
visualization tools with dedicated InSAR functionalities exist, that were designed to visualize a single radar 
image or interferogram.

However, recent spatial missions, like the Sentinel-1 mission of the European program 
COPERNICUS, with a systematic background acquisition strategy and an open data policy, 
provide unprecedented access to massive SAR datasets. From these new datasets, a network 
of thousands of interferograms can be generated over a single area. The consecutive step 
is a time-series analysis which produces a spatiotemporal data cube: a layer of this data 
cube is a 2D map that contains the displacement of each pixel of an image relative to the 
same pixel in the reference date image. A typical data cube size is 4000x6000x200, where 
4000x6000 are the spatial dimensions (pixels) and 200 is a typical number of images taken 
since the beginning of the spatial mission. 

The aforementioned tools are not suited to manage such large and multifaceted datasets. In 
particular, fluid and interactive data visualization of large, multidimensional datasets 
is non-trivial. If data cube visualization is a more generic problem and an active 
research topic in EO and beyond, some specifics of InSAR (radar geometry, wrapped phase, 
relative measurement in space and in time, multiple types of products needed for 
interpretation…) call for a new, dedicated visualization tool.
