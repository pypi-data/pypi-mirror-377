# 3D Visualization Tutorial

Comprehensive guide to creating immersive 3D visualizations with PlotX.

## Getting Started with 3D

PlotX provides powerful 3D visualization capabilities with advanced interaction support.

### Basic 3D Surface

```python
import plotx
import numpy as np

# Create 3D data
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# Create 3D surface plot
chart = plotx.SurfaceChart()
chart.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
chart.set_title('3D Surface: sin(√(x² + y²))')
chart.save('3d_surface.png')
```

### 3D Scatter Plot

```python
# Generate 3D point cloud
n_points = 1000
x = np.random.normal(0, 1, n_points)
y = np.random.normal(0, 1, n_points)
z = np.random.normal(0, 1, n_points)
colors = np.sqrt(x**2 + y**2 + z**2)

chart = plotx.Scatter3DChart()
chart.plot(x, y, z, c=colors, s=50, alpha=0.6, cmap='plasma')
chart.set_title('3D Point Cloud')
chart.save('3d_scatter.png')
```

## Interactive 3D Scenes

### Setting Up Interactive Scene

```python
import plotx.interaction3d as i3d

# Create interactive 3D scene
scene = i3d.Scene3D()

# Add objects to scene
cube = i3d.Cube(position=[0, 0, 0], size=2.0)
sphere = i3d.Sphere(position=[3, 0, 0], radius=1.0)
scene.add_objects([cube, sphere])

# Setup camera
camera = i3d.OrbitController(
    target=[1.5, 0, 0],
    distance=10.0,
    min_distance=2.0,
    max_distance=50.0
)
scene.set_camera(camera)

# Enable interaction
scene.enable_selection(mode="single")
scene.enable_manipulation(transforms=["translate", "rotate", "scale"])

# Start interactive session
scene.run()
```

### Advanced Camera Controls

```python
# Orbit camera - best for object inspection
orbit_camera = i3d.OrbitController(
    target=[0, 0, 0],        # Look at origin
    distance=15.0,           # Distance from target
    azimuth=45.0,           # Horizontal angle
    elevation=30.0,         # Vertical angle
    min_distance=5.0,
    max_distance=100.0
)

# Fly camera - best for navigation
fly_camera = i3d.FlyController(
    position=[10, 10, 10],
    target=[0, 0, 0],
    speed=5.0,
    acceleration=2.0
)

# First-person camera - best for immersion
fps_camera = i3d.FirstPersonController(
    position=[0, 2, 5],
    yaw=0.0,
    pitch=0.0,
    move_speed=3.0,
    look_speed=2.0
)

# Switch between cameras
scene.set_camera(orbit_camera)  # Start with orbit
```

### Gesture Recognition

```python
# Setup gesture recognition
gesture_recognizer = i3d.GestureRecognizer()

# Configure touch gestures
touch_handler = i3d.TouchHandler()
touch_handler.enable_pinch_zoom(sensitivity=1.0)
touch_handler.enable_rotation(sensitivity=0.5)
touch_handler.enable_pan(fingers=2)

# Configure mouse gestures
mouse_handler = i3d.MouseHandler()
mouse_handler.bind_orbit(button="left")
mouse_handler.bind_pan(button="middle")
mouse_handler.bind_zoom(wheel=True)

# Add to recognizer
gesture_recognizer.add_handler(touch_handler)
gesture_recognizer.add_handler(mouse_handler)

# Apply to scene
scene.set_gesture_recognizer(gesture_recognizer)
```

## Object Manipulation

### Selection System

```python
# Advanced selection configuration
selection_manager = i3d.SelectionManager()

# Ray-casting selection (precise)
raycast_selector = i3d.RaycastSelector()
raycast_selector.set_precision(0.01)  # 1cm precision

# Box selection (area select)
box_selector = i3d.BoxSelector()
box_selector.set_mode("intersect")  # or "contain"

# Add selectors
selection_manager.add_selector(raycast_selector)
selection_manager.add_selector(box_selector)

# Selection callbacks
@selection_manager.on_select
def on_object_selected(objects):
    print(f"Selected {len(objects)} objects")
    for obj in objects:
        obj.highlight(color="yellow")

@selection_manager.on_deselect
def on_object_deselected(objects):
    for obj in objects:
        obj.remove_highlight()

scene.set_selection_manager(selection_manager)
```

### Transform Gizmos

```python
# Create manipulation gizmo
gizmo = i3d.ManipulatorGizmo()

# Configure transform modes
gizmo.enable_translation(axes=["x", "y", "z"])
gizmo.enable_rotation(axes=["x", "y", "z"])
gizmo.enable_scaling(uniform=True)

# Customize appearance
gizmo.set_size(1.0)
gizmo.set_colors({
    "x_axis": "#FF0000",  # Red for X
    "y_axis": "#00FF00",  # Green for Y
    "z_axis": "#0000FF"   # Blue for Z
})

# Object manipulation
manipulator = i3d.ObjectManipulator()
manipulator.set_gizmo(gizmo)
manipulator.set_snap_to_grid(enabled=True, size=0.5)

scene.set_manipulator(manipulator)
```

## Animation System

### Keyframe Animation

```python
# Create animation timeline
animator = i3d.KeyFrameSystem()

# Animate cube rotation
cube_anim = animator.create_animation("cube_rotation")
cube_anim.add_keyframe(0.0, {"rotation": [0, 0, 0]})
cube_anim.add_keyframe(2.0, {"rotation": [0, 360, 0]})
cube_anim.add_keyframe(4.0, {"rotation": [360, 360, 0]})

# Animate camera movement
camera_anim = i3d.CameraAnimator(camera)
camera_anim.animate_to_position([10, 5, 10], duration=3.0)
camera_anim.animate_to_target([0, 0, 0], duration=3.0)

# Start animations
animator.play_all()
```

### Camera Animation

```python
# Smooth camera transitions
camera_animator = i3d.CameraAnimator(scene.camera)

# Predefined camera positions
positions = [
    {"position": [10, 0, 0], "target": [0, 0, 0]},   # Side view
    {"position": [0, 10, 0], "target": [0, 0, 0]},   # Top view
    {"position": [0, 0, 10], "target": [0, 0, 0]},   # Front view
    {"position": [7, 7, 7], "target": [0, 0, 0]}     # Isometric
]

# Animate through positions
for i, pos in enumerate(positions):
    camera_animator.animate_to_position(
        pos["position"],
        duration=2.0,
        delay=i*3.0,
        easing="ease_in_out"
    )
    camera_animator.animate_to_target(
        pos["target"],
        duration=2.0,
        delay=i*3.0
    )
```

## 3D Data Visualization

### Volumetric Data

```python
# Create volumetric dataset
x, y, z = np.mgrid[0:10:50j, 0:10:50j, 0:10:50j]
volume_data = np.sin(x) * np.cos(y) * np.sin(z)

# Volume rendering
volume_chart = plotx.VolumeChart()
volume_chart.plot_volume(volume_data, cmap='hot', alpha=0.3)
volume_chart.add_isosurfaces(levels=[0.1, 0.5, 0.9])
volume_chart.set_title('Volumetric Data Visualization')
```

### Scientific Visualization

```python
# Molecular visualization example
def create_molecule_scene():
    scene = i3d.Scene3D()

    # Atom positions (water molecule)
    atoms = [
        {"element": "O", "position": [0, 0, 0], "radius": 1.4},
        {"element": "H", "position": [1.5, 1.2, 0], "radius": 1.0},
        {"element": "H", "position": [-1.5, 1.2, 0], "radius": 1.0}
    ]

    # Atom colors
    colors = {"O": "#FF0000", "H": "#FFFFFF"}

    # Add atoms
    for atom in atoms:
        sphere = i3d.Sphere(
            position=atom["position"],
            radius=atom["radius"],
            color=colors[atom["element"]]
        )
        sphere.set_label(atom["element"])
        scene.add_object(sphere)

    # Add bonds
    bond1 = i3d.Cylinder(
        start=[0, 0, 0],
        end=[1.5, 1.2, 0],
        radius=0.2,
        color="#CCCCCC"
    )
    bond2 = i3d.Cylinder(
        start=[0, 0, 0],
        end=[-1.5, 1.2, 0],
        radius=0.2,
        color="#CCCCCC"
    )
    scene.add_objects([bond1, bond2])

    return scene

# Create and run molecular visualization
molecule_scene = create_molecule_scene()
molecule_scene.run()
```

### Engineering CAE Visualization

```python
# FEA mesh visualization
def create_fea_mesh():
    # Load mesh data (example with synthetic data)
    nodes = np.random.rand(1000, 3) * 10  # 1000 nodes
    elements = np.random.randint(0, 1000, (500, 4))  # 500 tetrahedral elements
    stress_values = np.random.rand(1000)  # Stress at each node

    # Create mesh visualization
    mesh_chart = plotx.MeshChart()
    mesh_chart.plot_mesh(nodes, elements,
                        scalar_field=stress_values,
                        cmap='jet',
                        show_edges=True,
                        edge_color='black',
                        edge_width=0.5)

    # Add color bar
    mesh_chart.add_colorbar(label='Von Mises Stress (MPa)')

    # Set view
    mesh_chart.set_camera_position([15, 15, 15])
    mesh_chart.set_title('FEA Stress Analysis')

    return mesh_chart

# Create and display FEA visualization
fea_viz = create_fea_mesh()
fea_viz.show_interactive()
```

## VR/AR Integration

### VR Setup

```python
# VR renderer setup
vr_renderer = i3d.VRRenderer()
vr_renderer.initialize(headset="oculus")  # or "vive", "index", etc.

# Create VR scene
vr_scene = i3d.Scene3D()
vr_scene.set_renderer(vr_renderer)

# Add VR-optimized objects
for i in range(20):
    obj = i3d.Cube(
        position=[np.random.uniform(-10, 10) for _ in range(3)],
        size=np.random.uniform(0.5, 2.0)
    )
    vr_scene.add_object(obj)

# VR interaction
vr_controller = i3d.VRController()
vr_controller.enable_hand_tracking()
vr_controller.enable_gesture_recognition()

vr_scene.set_controller(vr_controller)
vr_scene.start_vr_session()
```

### AR Overlay

```python
# AR renderer for mixed reality
ar_renderer = i3d.ARRenderer()
ar_renderer.initialize(device="hololens")  # or "magic_leap", "mobile"

# Create AR scene with real-world anchoring
ar_scene = i3d.Scene3D()
ar_scene.set_renderer(ar_renderer)

# Add virtual objects anchored to real world
virtual_chart = plotx.LineChart3D()
virtual_chart.plot_in_space(
    position=[0, 1, 2],  # 2 meters in front of user
    rotation=[0, 0, 0],
    scale=0.5
)

ar_scene.add_object(virtual_chart)
ar_scene.start_ar_session()
```

## Performance Optimization

### Level of Detail (LOD)

```python
# Configure LOD for large scenes
scene = i3d.Scene3D()

# LOD settings
lod_manager = i3d.LODManager()
lod_manager.set_distance_thresholds([10, 50, 100])  # meters
lod_manager.set_quality_levels(["high", "medium", "low"])

# Add objects with LOD
for i in range(1000):
    obj = i3d.ComplexMesh(f"object_{i}.obj")
    obj.generate_lod_levels(levels=3)
    scene.add_object(obj)

scene.set_lod_manager(lod_manager)
```

### Frustum Culling

```python
# Enable frustum culling for performance
frustum_culler = i3d.FrustumCuller()
frustum_culler.enable_occlusion_culling(True)
frustum_culler.set_culling_distance(1000.0)

scene.set_frustum_culler(frustum_culler)
```

### GPU Acceleration

```python
# Enable GPU rendering
scene = i3d.Scene3D(renderer="opengl")  # or "vulkan", "metal"

# GPU-accelerated operations
scene.enable_gpu_culling(True)
scene.enable_gpu_lighting(True)
scene.enable_gpu_shadows(True)
```

## Advanced Features

### Multi-Scene Management

```python
# Scene manager for complex applications
scene_manager = i3d.SceneManager()

# Create multiple scenes
main_scene = i3d.Scene3D()
ui_scene = i3d.Scene3D()  # For UI elements
background_scene = i3d.Scene3D()  # For environment

# Add scenes to manager
scene_manager.add_scene("main", main_scene)
scene_manager.add_scene("ui", ui_scene)
scene_manager.add_scene("background", background_scene)

# Set render order
scene_manager.set_render_order(["background", "main", "ui"])

# Switch active scene
scene_manager.set_active_scene("main")
```

### Spatial Audio

```python
# Add spatial audio to 3D scene
audio_system = i3d.SpatialAudioSystem()

# Add positional audio sources
audio_source = i3d.AudioSource("ambient.wav")
audio_source.set_position([5, 0, 0])
audio_source.set_falloff_distance(10.0)

scene.add_audio_source(audio_source)
scene.set_audio_system(audio_system)
```

### Physics Integration

```python
# Add physics simulation
physics_engine = i3d.PhysicsEngine()
physics_engine.set_gravity([0, -9.81, 0])

# Add physics objects
rigid_body = i3d.RigidBody(cube)
rigid_body.set_mass(1.0)
rigid_body.set_restitution(0.8)

physics_engine.add_rigid_body(rigid_body)
scene.set_physics_engine(physics_engine)

# Start physics simulation
physics_engine.start()
```

## Best Practices

### Performance Guidelines

1. **Object Management**: Use object pooling for dynamic scenes
2. **Rendering**: Enable frustum culling and LOD
3. **Memory**: Clear unused objects regularly
4. **GPU**: Use GPU acceleration when available

### User Experience

1. **Navigation**: Provide multiple camera modes
2. **Selection**: Clear visual feedback for interactions
3. **Performance**: Maintain 60+ FPS for smooth interaction
4. **Accessibility**: Support keyboard navigation

### Code Organization

```python
class Custom3DApp:
    def __init__(self):
        self.scene = i3d.Scene3D()
        self.setup_camera()
        self.setup_interaction()
        self.setup_objects()

    def setup_camera(self):
        self.camera = i3d.OrbitController()
        self.scene.set_camera(self.camera)

    def setup_interaction(self):
        self.scene.enable_selection()
        self.scene.enable_manipulation()

    def setup_objects(self):
        # Add your 3D objects here
        pass

    def run(self):
        self.scene.run()

# Usage
app = Custom3DApp()
app.run()
```

## Next Steps

- Explore [VR/AR Development](vr-ar-development.md)
- Learn about [Real-time Applications](real-time-applications.md)
- Check out [3D Examples Gallery](../examples/3d-gallery.md)

---

Ready for immersive 3D experiences? Continue with our specialized 3D tutorials!