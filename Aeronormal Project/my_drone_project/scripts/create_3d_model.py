import numpy as np
import os
from pythreejs import *
from IPython.display import display

def create_3d_model(point_cloud_file):
    points = np.loadtxt(point_cloud_file)
    geometry = BufferGeometry(attributes={
        'position': BufferAttribute(points, normalized=False),
    })

    material = PointsMaterial(size=0.05, color='blue')
    points = Points(geometry=geometry, material=material)

    scene = Scene(children=[points, AmbientLight(color='#777777')])
    camera = PerspectiveCamera(position=[0, 0, 2], aspect=800 / 600)
    renderer = Renderer(camera=camera, scene=scene, controls=[OrbitControls(controlling=camera)])

    display(renderer)

if __name__ == "__main__":
    point_cloud_file = os.path.join(os.path.dirname(__file__), "../data/pointcloud/pointcloud.txt")
    create_3d_model(point_cloud_file)