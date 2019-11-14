# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

""" Simple demonstration of the new 3D visualization tool for Madagascar.
The program displays x-, y-, z- slices of a numpy array in 3D, allows user
to interactively drag the slices, includes useful features such as colorbar
and axis legend, and can output the figure to .png file with various resolution.
"""

import numpy as np

from seismic_canvas import (SeismicCanvas, volume_slices, XYZAxis, Colorbar)


if __name__ == '__main__':

  # # Test 1: seismic image data.
  # # 1. F3 seismic
  # # volume = np.fromfile('./F3_seismic.dat', '>f4').reshape(420, 400, 100)
  # # volume = np.memmap('./F3_seismic.dat', dtype='>f4',
  # #                  mode='r', shape=(420, 400, 100))
  # # 2. Costa Rica seismic
  # # volume = np.fromfile('./CostaRica_seismic.dat', '>f4').reshape(825, 920, 210)
  # volume = np.memmap('./CostaRica_seismic.dat', dtype='>f4',
  #                    mode='r', shape=(825, 920, 210))
  # axis_scales = (1, 1, 1.5) # anisotropic axes (stretch z-axis)

  # # Colormaps.
  # cmap='grays'; clim=(-2, 2)
  # # Get visual nodes ready.
  # visual_nodes = volume_slices(volume,
  #   cmaps=cmap, clims=clim,
  #   # x_pos=32, y_pos=25, z_pos=93)
  #   x_pos=[370, 170, 570, 770], y_pos=810, z_pos=120)
  # xyz_axis = XYZAxis()
  # colorbar = Colorbar(cmap=cmap, clim=clim, label_str='Seismic Amplitude',
  #                     label_size=8, tick_size=6)


  # Test 2: brain CT data.
  from vispy import io
  volume = np.load(io.load_data_file('brain/mri.npz'))['data']
  volume = volume.transpose(2, 0, 1)[:, :, ::-1]
  axis_scales = (1, 1, 1) # isotropoic axes

  visual_nodes = volume_slices(volume,
    x_pos=100, y_pos=128, z_pos=30,
    seismic_coord_system=False)
  xyz_axis = XYZAxis(seismic_coord_system=False)
  colorbar = Colorbar(cmap='grays', clim=(volume.min(), volume.max()),
                      label_str='Amplitude', label_size=8, tick_size=6)


  # Run the canvas.
  canvas = SeismicCanvas(title='Simple Demo',
                         visual_nodes=visual_nodes,
                         xyz_axis=xyz_axis,
                         colorbar=colorbar,
                         # Set the option below=0 will hide the colorbar region
                         # colorbar_region_ratio=0,
                         axis_scales=axis_scales,
                         # Manual camera setting below.
                         # auto_range=False,
                         # scale_factor=972.794,
                         # center=(434.46, 545.63, 10.26),
                         fov=30,
                         elevation=36,
                         azimuth=45,
                         zoom_factor=1.2 # >1: zoom in; <1: zoom out
                         )
  canvas.measure_fps()
  canvas.app.run()
