from vispy import scene
import numpy as np

c = scene.SceneCanvas(keys='interactive', show=True)

view = c.central_widget.add_view()
view.camera = 'fly'
view.camera.depth = 10

pos = np.array([(0, 0, 0), (2, 1, 1)])
s = scene.Markers(pos=pos, parent=view.scene)
s.interactive = True

@c.connect
def on_mouse_press(event):
    view.interactive = False
    what = c.visual_at(event.pos)
    if what is not None:
        print(dir(what))
    view.interactive = True

c.app.run()
