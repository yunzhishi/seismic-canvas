# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
