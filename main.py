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

""" Simple demonstration of the new 3D visualization tool for Madagascar.
The program displays x-, y-, z- slices of a numpy array in 3D, allows user
to interactively drag the slices, includes useful features such as colorbar
and axis legend, and can output the figure to .png file with various resolution.
"""

from seismic_canvas import (SeismicCanvas, volume_slices, XYZAxis)


if __name__ == '__main__':

  # Test 1: seismic image data.
  import numpy as np
  # volume = np.fromfile('./F3_seismic.dat', '>f4').reshape(420, 400, 100)
  # volume = np.memmap('./F3_seismic.dat', dtype='>f4',
  #                    mode='r', shape=(420, 400, 100))
  # volume = np.fromfile('./CostaRica_seismic.dat', '>f4').reshape(825, 920, 210)
  volume = np.memmap('./CostaRica_seismic.dat', dtype='>f4',
                     mode='r', shape=(825, 920, 210))

  # Collect all visual nodes.
  visual_nodes = volume_slices(volume,
    # x_pos=50, y_pos=50, z_pos=90, clim=(-2, 2))
    x_pos=[370, 170, 570, 770], y_pos=810, z_pos=120, clim=(-2, 2))

  # Add an axis legend.
  xyz_axis = XYZAxis()


  # # Test 2: brain CT data.
  # import numpy as np
  # from vispy import io
  # volume = np.load(io.load_data_file('brain/mri.npz'))['data']
  # volume = volume.transpose(2, 0, 1)[:, :, ::-1]

  # # Collect all visual nodes.
  # visual_nodes = volume_slices(volume,
  #   x_pos=100, y_pos=128, z_pos=30,
  #   seismic_coord_system=False)

  # # Add an axis legend.
  # xyz_axis = XYZAxis(seismic_coord_system=False)


  # Run the canvas.
  canvas = SeismicCanvas(visual_nodes=visual_nodes, xyz_axis=xyz_axis)
  canvas.measure_fps()
  canvas.app.run()
