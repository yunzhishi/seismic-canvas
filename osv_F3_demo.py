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

""" A demonstration of the new 3D visualization tool applied to the research
'Optimal Surface Voting': https://github.com/xinwucwp/osv.
"""

import numpy as np
from vispy.color import get_colormap, Colormap

from seismic_canvas import (SeismicCanvas, volume_slices, XYZAxis, Colorbar)


if __name__ == '__main__':

  # Image 1: seismic overlaid by planarity attribute.
  seismic_vol = np.memmap('./F3_seismic.dat', dtype='>f4',
                          mode='r', shape=(420, 400, 100))
  planarity_vol = np.memmap('./F3_planarity.dat', dtype='>f4',
                            mode='r', shape=(420, 400, 100))
  axis_scales = (1, 1, 1.5) # anisotropic axes (stretch z-axis)

  seismic_cmap = 'grays'
  seismic_range = (-2.0, 2.0)
  # Get a colormap with alpha decreasing when value decreases.
  planarity_cmap = Colormap([[1,1,1, 0], [1,1,0, 0.5], [1,0,0, 1]])
  planarity_range = (0.25, 1.0)

  visual_nodes = volume_slices([seismic_vol, planarity_vol],
    cmaps=[seismic_cmap, planarity_cmap],
    clims=[seismic_range, planarity_range],
    # The preprocessing functions can perform some simple gaining ops.
    preproc_funcs=[None, lambda x: 1-np.power(x, 8)],
    x_pos=32, y_pos=25, z_pos=93)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=planarity_cmap, clim=planarity_range,
                      label_str='1 - Planarity')

  canvas1 = SeismicCanvas(title='Planarity',
                          size=(800, 600),
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          # Set the option below=0 will hide the colorbar region.
                          # colorbar_region_ratio=0,
                          axis_scales=axis_scales,
                          # Manual camera setting below.
                          # auto_range=False,
                          # scale_factor=972.794,
                          # center=(434.46, 545.63, 10.26),
                          fov=30,
                          elevation=36,
                          azimuth=45,
                          )
  canvas1.camera.scale_factor /= 1.6 # >1: zoom in; <1: zoom out
  canvas1.app.run()
