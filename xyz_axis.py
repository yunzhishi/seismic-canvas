# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy import scene
from vispy.visuals.transforms import MatrixTransform


class XYZAxis(scene.visuals.XYZAxis):
  """ An XYZAxis legend visual that add some interactivity fixes to be used
  in 3D. It rotates correctly, and can be dragged around.

  Parameters:

  """
  def __init__(self, loc=(60, 60), size=50, visible=True,
               width=2, antialias=True, parent=None):
    # Create a scene.visuals.XYZAxis (without parent by default).
    scene.visuals.XYZAxis.__init__(self, parent=parent,
                                   width=width, antialias=antialias)
    self.unfreeze()
    self.interactive = False
    self.visible = visible

    # The axis legend is rotated to align with the parent camera. Then put
    # the legend to specified location and scale up to desired size.
    # The location is computed from the top-left corner.
    self.loc = loc
    self.size = size
    self.transform = MatrixTransform()
    self.update_axis()

    self.freeze()

  def on_mouse_move(self, event):
    if event.button == 1 and event.is_dragging:
      self.update_axis()

  def update_axis(self):
    """ Align the axis legend with the current camera rotation, scale up to
    desired size, then put the axis legend at pos (measuring from the
    top-left corner).
    """
    if self.parent is None:
      return # if not connected to any parent, no need to update

    tr = self.transform
    tr.reset() # remove all transforms (put back to origin)

    # Align camera rotation. This only works for turntable camera!!
    tr.rotate(90, (1, 0, 0)) # for some reason I have to do this at first ...
    tr.rotate(self.parent.camera.azimuth, (0, 1, 0))
    tr.rotate(self.parent.camera.elevation, (1, 0, 0))
    # Scale up to desired size and put to desired location.
    tr.scale((*(self.size,)*2, 0.001)) # only scale in screen plane!
    tr.translate(self.loc)

    self.update()
