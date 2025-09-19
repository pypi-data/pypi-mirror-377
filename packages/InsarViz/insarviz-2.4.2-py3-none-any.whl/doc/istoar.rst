ISTerre users: work on ist-oar
==============================

This section is for ISTerre members only.

InsarViz is installed on ist-oar.

First, log in through ssh:

.. code-block :: bash

 ssh -Y ist-oar

Then either work directly on the front-end processor:

.. code-block :: bash

 source /usr/contrib/cycle/venv-insarviz/bin/activate
 	
 ts_viz

Or request a visualisation node:

.. code-block :: bash

 oarsub -I --project cime-pos-isdeform

 source /usr/contrib/cycle/venv-insarviz/bin/activate
 
 ts_viz

A beta version of insarviz is also available:

.. code-block :: bash

 source /usr/contrib/cycle/venv-insarviz-beta/bin/activate
 	
 ts_viz
