# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from .seismic_canvas import SeismicCanvas
from .axis_aligned_image import AxisAlignedImage
from .volume_slices import volume_slices
from .xyz_axis import XYZAxis

try:
  # Check Python module dependencies.
  import matplotlib.pyplot
  # Only import the MPL generated colorbar if MPL is available.
  from .colorbar_MPL import Colorbar
except ImportError:
  from warnings import warn
  warn("Module matplotlib/tkinter missing, using vispy stock colorbar")
  # Use vispy stock colorbar if MPL is not available.
  from .colorbar import Colorbar
