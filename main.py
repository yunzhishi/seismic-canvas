# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Simple demonstration of the new 3D visualization tool for Madagascar.
The program displays x-, y-, z- slices of a numpy array in 3D, allows user
to interactively drag the slices, includes useful features such as colorbar
and axis legend, and can output the figure to .png file with various resolution.
"""

from vispy import app

from volume_slices import volume_slices
from xyz_axis import XYZAxis
from seismic_canvas import SeismicCanvas


if __name__ == '__main__':
  # Prepare the image data.
  from vispy import io
  import numpy as np
  volume = np.load(io.load_data_file('brain/mri.npz'))['data']
  volume = np.flipud(np.rollaxis(volume, 1)) # rotate volume

  # Collect all visual nodes.
  visual_nodes = volume_slices(volume,
    x_pos=10, y_pos=20, z_pos=30)

  # Add an axis legend.
  xyz_axis = XYZAxis()

  # Run the canvas.
  canvas = SeismicCanvas(visual_nodes=visual_nodes, xyz_axis=xyz_axis)
  app.run()
