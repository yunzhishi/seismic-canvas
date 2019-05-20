# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Simple demonstration of the new 3D visualization tool for Madagascar.
The program displays x-, y-, z- slices of a numpy array in 3D, allows user
to interactively drag the slices, includes useful features such as colorbar
and axis legend, and can output the figure to .png file with various resolution.
"""

from vispy import app

from get_image import get_image
from axis_aligned_image import AxisAlignedImage
from xyz_axis import XYZAxis
from seismic_canvas import SeismicCanvas


if __name__ == '__main__':
  # Prepare the image data.
  image = get_image()
  import numpy as np
  scale_x = np.linspace(1., 0., image.shape[0])[..., np.newaxis, np.newaxis]
  scale_y = np.linspace(1., 0., image.shape[1])[np.newaxis, ..., np.newaxis]
  image = (image * scale_x * scale_y).astype(np.ubyte)

  # Collect all visual nodes.
  visual_nodes = []
  image_node_z = AxisAlignedImage(image, pos=30)
  visual_nodes.append(image_node_z)
  image_node_y = AxisAlignedImage(image, axis='y', pos=20)
  visual_nodes.append(image_node_y)
  image_node_x = AxisAlignedImage(image, axis='x', pos=10)
  visual_nodes.append(image_node_x)

  # Add an axis legend.
  xyz_axis = XYZAxis()

  # Run the canvas.
  canvas = SeismicCanvas(visual_nodes=visual_nodes, xyz_axis=xyz_axis)
  app.run()
