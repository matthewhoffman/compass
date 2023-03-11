.. _dev_landice_framework:

Land-ice Framework
==================

ais_observations
~~~~~~~~~~~~~~~~

The landice framework module ``compass/landice/ais_observations.py`` contains
observational data for various Antarctic basins.  These are based on the
ISMIP6 basin definitions, but it need not be limited to those.  The basins do
not need to be mutually exclusive, so more can be added as needed.

extrapolate
~~~~~~~~~~~

The landice framework module ``compass/landice/extrapolate.py`` provides a
function for extrapolating variables into undefined regions.  It is copied
from a similar script in MPAS-Tools.

icshelf_melt
~~~~~~~~~~~~
The landice framework module ``compass/landice/iceshelf_melt.py`` provides
functionality related to ice-shelf basal melting.  Currently, there is a
single function ``calc_mean_TF`` that calculated the mean thermal forcing
along the ice-shelf draft in a domain for a given geometry file and thermal
forcing file.

