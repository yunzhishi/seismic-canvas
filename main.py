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

  # # Test 1: seismic image data.
  # import numpy as np
  # # volume = np.fromfile('./F3_seismic.dat', '>f4').reshape(420, 400, 100)
  # volume = np.fromfile('./CostaRica_seismic.dat', '>f4').reshape(825, 920, 210)

  # # Collect all visual nodes.
  # visual_nodes = volume_slices(volume,
  #   x_pos=370, y_pos=810, z_pos=120, clim=(-2, 2))

  # # Add an axis legend.
  # xyz_axis = XYZAxis()


  # Test 2: brain CT data.
  import numpy as np
  from vispy import io
  volume = np.load(io.load_data_file('brain/mri.npz'))['data']
  volume = volume.transpose(2, 0, 1)[:, :, ::-1]

  # Collect all visual nodes.
  visual_nodes = volume_slices(volume,
    x_pos=100, y_pos=128, z_pos=30,
    seismic_coord_system=False)

  # Add an axis legend.
  xyz_axis = XYZAxis(seismic_coord_system=False)


  # Run the canvas.
  canvas = SeismicCanvas(visual_nodes=visual_nodes, xyz_axis=xyz_axis)
  canvas.camera.azimuth = 120
  canvas.measure_fps()
  app.run()
