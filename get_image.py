# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from vispy.io import load_data_file, read_png


def get_image():
  """Load an image from the demo-data repository if possible. Otherwise,
  just return a randomly generated image.
  """
  try:
    return read_png(load_data_file('mona_lisa/mona_lisa_sm.png'))
  except Exception as exc:
    # Fall back to random image.
    print("Error loading demo image data: %r" % exc)

  # Generate random image.
  image = np.random.normal(size=(100, 100, 3))
  image[20:80, 20:80] += 3.
  image[50] += 3.
  image[:, 50] += 3.
  image = ((image - image.min()) *
           (253. / (image.max() - image.min()))).astype(np.ubyte)
  return image
