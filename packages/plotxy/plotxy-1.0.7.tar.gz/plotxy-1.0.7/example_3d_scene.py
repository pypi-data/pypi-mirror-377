#!/usr/bin/env python3
"""
Working example of PlotXY 3D Scene
This demonstrates the fixed 3D interaction functionality.
"""

import plotxy
from plotxy import interaction3d as i3d
import numpy as np

def main():
    print("🚀 PlotXY 3D Scene Example")
    print("=" * 40)

    # Create interactive 3D scene
    scene = i3d.Scene3D()

    # Add objects
    cube = i3d.Cube(position=np.array([0, 0, 0]), size=2.0)
    sphere = i3d.Sphere(position=np.array([3, 0, 0]), radius=1.0)

    # Set different colors
    cube.set_material_property('color', np.array([1.0, 0.0, 0.0]))  # Red
    sphere.set_material_property('color', np.array([0.0, 0.0, 1.0]))  # Blue

    # Add objects to scene
    object_ids = scene.add_objects([cube, sphere])
    print(f"Added objects: {object_ids}")

    # Setup camera controls
    camera = i3d.OrbitController(target=np.array([1.5, 0, 0]), distance=10.0)
    scene.set_camera(camera)

    # Enable interaction
    scene.enable_selection(mode="multiple")
    scene.enable_manipulation(transforms=["translate", "rotate", "scale"])

    # Print scene information
    print(f"Scene bounds: {scene.get_scene_bounds()}")
    print(f"Object count: {len(scene.objects)}")

    # Focus camera on scene
    scene.focus_camera_on_scene()

    # Start interactive session
    print("\n🎮 Starting 3D scene...")
    scene.run()

    print("\n✅ 3D Scene example completed successfully!")
    return True

if __name__ == "__main__":
    main()