# 3D Interaction API Reference

Complete API documentation for PlotX's advanced 3D interaction system.

## Camera Controllers

### OrbitController

CAD-style camera navigation around a target point.

```python
class OrbitController:
    """Orbit camera controller for CAD-style navigation."""

    def __init__(self, position: np.ndarray = None, target: np.ndarray = None,
                 distance: float = 5.0):
        """Initialize orbit controller.

        Args:
            position: Initial camera position
            target: Look-at target point
            distance: Distance from target
        """

    def update(self, dt: float, mouse_dx: float = 0, mouse_dy: float = 0,
               scroll_delta: float = 0, keys_pressed: set = None) -> None:
        """Update camera based on input.

        Args:
            dt: Delta time in seconds
            mouse_dx: Mouse movement in X
            mouse_dy: Mouse movement in Y
            scroll_delta: Scroll wheel delta
            keys_pressed: Set of pressed keys
        """

    def focus_on_bounds(self, min_bounds: np.ndarray, max_bounds: np.ndarray):
        """Focus camera to fit bounding box."""

    def set_constraints(self, min_distance: float = 0.1, max_distance: float = 100.0,
                       min_elevation: float = -89.0, max_elevation: float = 89.0):
        """Set movement constraints."""

    # Properties
    @property
    def position(self) -> np.ndarray:
        """Current camera position."""

    @property
    def target(self) -> np.ndarray:
        """Current look-at target."""

    @property
    def distance(self) -> float:
        """Current distance from target."""
```

**Example Usage:**

```python
import plotx
import numpy as np

# Create 3D scene with orbit camera
scene = plotx.Scene3D()
camera = plotx.OrbitController(distance=10.0)

# Configure camera constraints
camera.set_constraints(
    min_distance=1.0,
    max_distance=50.0,
    min_elevation=-60.0,
    max_elevation=80.0
)

# Add to scene
scene.set_camera(camera)

# Focus on specific objects
bounds_min = np.array([-5, -5, -5])
bounds_max = np.array([5, 5, 5])
camera.focus_on_bounds(bounds_min, bounds_max)
```

### FlyController

Free-flying camera for exploration.

```python
class FlyController:
    """Free-flying camera controller."""

    def __init__(self, position: np.ndarray = None, target: np.ndarray = None):
        """Initialize fly controller."""

    def update(self, dt: float, mouse_dx: float = 0, mouse_dy: float = 0,
               scroll_delta: float = 0, keys_pressed: set = None) -> None:
        """Update camera with WASD movement."""

    def set_movement_speed(self, speed: float, sprint_multiplier: float = 3.0):
        """Set movement speeds."""

    def set_look_sensitivity(self, sensitivity: float):
        """Set mouse look sensitivity."""
```

**Example Usage:**

```python
# Free-flying camera
fly_camera = plotx.FlyController(position=np.array([0, 5, 10]))
fly_camera.set_movement_speed(speed=5.0, sprint_multiplier=2.0)
fly_camera.set_look_sensitivity(0.1)

scene.set_camera(fly_camera)

# Input handling
keys_pressed = {'w', 'shift'}  # Moving forward with sprint
fly_camera.update(dt=0.016, mouse_dx=5, mouse_dy=-2, keys_pressed=keys_pressed)
```

### FirstPersonController

Ground-constrained first-person navigation.

```python
class FirstPersonController:
    """First-person camera with ground constraints."""

    def __init__(self, position: np.ndarray = None, eye_height: float = 1.8):
        """Initialize FPS controller."""

    def set_ground_level(self, ground_y: float):
        """Set ground level for physics."""

    def enable_physics(self, gravity: float = -9.81, jump_velocity: float = 5.0):
        """Enable physics simulation."""
```

## Gesture Recognition

### GestureRecognizer

Multi-touch and mouse gesture recognition.

```python
class GestureRecognizer:
    """Advanced gesture recognition system."""

    def __init__(self, viewport_width: int = 800, viewport_height: int = 600):
        """Initialize gesture recognizer."""

    def add_gesture_callback(self, gesture_type: GestureType, callback: Callable):
        """Register gesture callback.

        Args:
            gesture_type: Type of gesture to detect
            callback: Function to call when gesture detected
        """

    def process_touch_down(self, touch_id: int, x: float, y: float, pressure: float = 1.0):
        """Process touch start event."""

    def process_touch_move(self, touch_id: int, x: float, y: float, pressure: float = 1.0):
        """Process touch movement."""

    def process_touch_up(self, touch_id: int, x: float, y: float):
        """Process touch end event."""
```

**Supported Gesture Types:**

```python
class GestureType(Enum):
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    DRAG = "drag"
    PINCH = "pinch"
    ROTATE = "rotate"
    SWIPE = "swipe"
    PAN = "pan"
    ZOOM = "zoom"
```

**Example Usage:**

```python
# Setup gesture recognition
recognizer = plotx.GestureRecognizer(800, 600)

# Define gesture handlers
def on_pinch(gesture):
    scale = gesture.scale
    camera.distance *= (2.0 - scale)  # Zoom

def on_drag(gesture):
    dx, dy = gesture.velocity
    camera.rotate(dx * 0.01, dy * 0.01)

def on_tap(gesture):
    # Select object at tap location
    x, y = gesture.start_position
    selected = selection_manager.select_by_screen_point(x, y)

# Register callbacks
recognizer.add_gesture_callback(GestureType.PINCH, on_pinch)
recognizer.add_gesture_callback(GestureType.DRAG, on_drag)
recognizer.add_gesture_callback(GestureType.TAP, on_tap)

# Process input events
recognizer.process_touch_down(1, 400, 300)
recognizer.process_touch_move(1, 420, 310)
recognizer.process_touch_up(1, 420, 310)
```

## Object Selection

### SelectionManager

Advanced 3D object selection system.

```python
class SelectionManager:
    """3D object selection with multiple methods."""

    def __init__(self):
        """Initialize selection manager."""

    def add_object(self, obj: SelectableObject):
        """Add object to selection system."""

    def set_selection_mode(self, mode: SelectionMode):
        """Set selection behavior."""

    def select_by_ray(self, ray: Ray, max_distance: float = float('inf')) -> List[str]:
        """Select objects intersected by ray."""

    def select_by_screen_point(self, screen_x: float, screen_y: float,
                              viewport_width: int, viewport_height: int,
                              view_matrix: np.ndarray,
                              projection_matrix: np.ndarray) -> List[str]:
        """Select object at screen coordinates."""

    def select_by_box(self, min_corner: np.ndarray, max_corner: np.ndarray) -> List[str]:
        """Select objects within 3D box."""

    def select_by_screen_box(self, start_x: float, start_y: float,
                            end_x: float, end_y: float,
                            viewport_width: int, viewport_height: int,
                            view_matrix: np.ndarray,
                            projection_matrix: np.ndarray) -> List[str]:
        """Box selection from screen coordinates."""
```

**Selection Modes:**

```python
class SelectionMode(Enum):
    SINGLE = "single"      # Select one object
    MULTIPLE = "multiple"  # Select multiple objects
    ADDITIVE = "additive"  # Add to selection
    SUBTRACTIVE = "subtractive"  # Remove from selection
```

**Example Usage:**

```python
# Setup selection
selection = plotx.SelectionManager()
selection.set_selection_mode(plotx.SelectionMode.MULTIPLE)

# Add selectable objects
for i, mesh in enumerate(scene_meshes):
    obj = plotx.SelectableObject(
        id=f"mesh_{i}",
        position=mesh.position,
        bounding_box=mesh.get_bounds()
    )
    selection.add_object(obj)

# Select objects
selected = selection.select_by_screen_point(400, 300, 800, 600,
                                           view_matrix, proj_matrix)

# Box selection
box_selected = selection.select_by_screen_box(200, 200, 600, 400,
                                             800, 600, view_matrix, proj_matrix)

# Get selected objects
current_selection = selection.get_selected_objects()
print(f"Selected {len(current_selection)} objects")
```

## Object Manipulation

### Transform3D

3D transformation matrix operations.

```python
class Transform3D:
    """3D transformation with position, rotation, and scale."""

    def __init__(self, position: np.ndarray = None,
                 rotation: np.ndarray = None,
                 scale: np.ndarray = None):
        """Initialize transform.

        Args:
            position: 3D position vector
            rotation: Euler angles (radians)
            scale: 3D scale vector
        """

    def translate(self, offset: np.ndarray):
        """Apply translation offset."""

    def rotate(self, angles: np.ndarray):
        """Apply rotation (Euler angles)."""

    def scale_by(self, factors: np.ndarray):
        """Apply scaling factors."""

    def transform_point(self, point: np.ndarray) -> np.ndarray:
        """Transform a 3D point."""

    def transform_vector(self, vector: np.ndarray) -> np.ndarray:
        """Transform a direction vector."""

    @property
    def matrix(self) -> np.ndarray:
        """Get 4x4 transformation matrix."""

    @property
    def inverse_matrix(self) -> np.ndarray:
        """Get inverse transformation matrix."""
```

### ManipulatorGizmo

Visual 3D manipulation handles.

```python
class ManipulatorGizmo:
    """3D manipulation gizmo for interactive transformation."""

    def __init__(self, transform: Transform3D):
        """Initialize gizmo for transform."""

    def set_mode(self, mode: TransformMode):
        """Set manipulation mode."""

    def set_constraint(self, constraint: AxisConstraint):
        """Set axis constraint."""

    def start_interaction(self, screen_pos: Tuple[float, float],
                         ray_origin: np.ndarray,
                         ray_direction: np.ndarray) -> bool:
        """Start manipulation interaction."""

    def update_interaction(self, screen_pos: Tuple[float, float],
                          ray_origin: np.ndarray,
                          ray_direction: np.ndarray):
        """Update manipulation based on mouse movement."""

    def end_interaction(self):
        """End manipulation interaction."""

    def get_gizmo_geometry(self) -> Dict[str, Any]:
        """Get geometry data for rendering gizmo."""
```

**Transform Modes:**

```python
class TransformMode(Enum):
    TRANSLATE = "translate"
    ROTATE = "rotate"
    SCALE = "scale"
    COMBINED = "combined"
```

**Axis Constraints:**

```python
class AxisConstraint(Enum):
    NONE = "none"
    X_AXIS = "x"
    Y_AXIS = "y"
    Z_AXIS = "z"
    XY_PLANE = "xy"
    XZ_PLANE = "xz"
    YZ_PLANE = "yz"
    SCREEN_SPACE = "screen"
```

**Example Usage:**

```python
# Create transform and gizmo
transform = plotx.Transform3D(position=np.array([0, 0, 0]))
gizmo = plotx.ManipulatorGizmo(transform)

# Set manipulation mode
gizmo.set_mode(plotx.TransformMode.TRANSLATE)
gizmo.set_constraint(plotx.AxisConstraint.XY_PLANE)

# Handle interaction
ray_origin = camera.position
ray_direction = camera.get_ray_direction(mouse_x, mouse_y)

if gizmo.start_interaction((mouse_x, mouse_y), ray_origin, ray_direction):
    # Update during drag
    gizmo.update_interaction((new_mouse_x, new_mouse_y), ray_origin, ray_direction)

    # End on mouse release
    gizmo.end_interaction()
```

## Navigation System

### NavigationController

Advanced pathfinding and camera navigation.

```python
class NavigationController:
    """High-level navigation system."""

    def __init__(self, camera_controller=None):
        """Initialize navigation with camera."""

    def navigate_to_position(self, target_position: np.ndarray,
                           algorithm: str = 'astar') -> bool:
        """Navigate to specific position."""

    def follow_waypoints(self, waypoints: List[Waypoint]) -> bool:
        """Follow sequence of waypoints."""

    def start_guided_tour(self, tour_waypoints: List[Waypoint],
                         auto_advance: bool = True) -> bool:
        """Start automated tour."""

    def create_orbit_path(self, center: np.ndarray, radius: float,
                         height: float, num_points: int = 16) -> List[Waypoint]:
        """Create circular orbit path."""

    def create_flyby_path(self, targets: List[np.ndarray],
                         viewing_distance: float = 10.0) -> List[Waypoint]:
        """Create flyby path through targets."""
```

### Waypoint

Navigation waypoint with timing and metadata.

```python
@dataclass
class Waypoint:
    """Navigation waypoint."""

    position: np.ndarray
    orientation: np.ndarray = None  # Quaternion
    name: str = ""
    description: str = ""
    duration: float = 2.0  # Time to stay
    transition_time: float = 1.0  # Travel time
    metadata: Dict[str, Any] = None

    @classmethod
    def from_position_target(cls, position: np.ndarray,
                           target: np.ndarray,
                           up: np.ndarray = None) -> 'Waypoint':
        """Create waypoint looking at target."""
```

**Example Usage:**

```python
# Create navigation system
nav = plotx.NavigationController(camera)

# Create waypoints for tour
waypoints = [
    plotx.Waypoint.from_position_target(
        position=np.array([10, 5, 10]),
        target=np.array([0, 0, 0]),
        duration=3.0
    ),
    plotx.Waypoint.from_position_target(
        position=np.array([-10, 8, 5]),
        target=np.array([0, 0, 0]),
        duration=2.0
    )
]

# Start guided tour
nav.start_guided_tour(waypoints, auto_advance=True)

# Create orbit path
orbit_waypoints = nav.create_orbit_path(
    center=np.array([0, 0, 0]),
    radius=15.0,
    height=5.0,
    num_points=20
)

nav.follow_waypoints(orbit_waypoints)
```

## Animation System

### CameraAnimator

Smooth camera animation and transitions.

```python
class CameraAnimator:
    """Camera animation system."""

    def __init__(self, camera_controller=None):
        """Initialize with camera."""

    def create_orbit_animation(self, name: str, center: np.ndarray,
                              radius: float, height: float,
                              duration: float, revolutions: int = 1) -> Animation:
        """Create orbital camera animation."""

    def create_flythrough_animation(self, name: str,
                                   waypoints: List[Tuple[np.ndarray, np.ndarray]],
                                   duration: float, smooth: bool = True) -> Animation:
        """Create flythrough animation."""

    def create_focus_animation(self, name: str, target_position: np.ndarray,
                              distance: float, duration: float) -> Animation:
        """Create focus animation."""

    def play_animation(self, name: str, loop: bool = False) -> bool:
        """Play named animation."""

    def stop_animation(self):
        """Stop current animation."""
```

### KeyFrameSystem

Timeline-based animation system.

```python
class KeyFrameSystem:
    """Advanced keyframe animation."""

    def create_timeline_animation(self, name: str, start_time: float = 0.0) -> Animation:
        """Create animation on timeline."""

    def play_timeline(self, loop: bool = False):
        """Play entire timeline."""

    def set_loop_region(self, start_time: float, end_time: float):
        """Set loop region."""
```

**Example Usage:**

```python
# Camera animation
animator = plotx.CameraAnimator(camera)

# Create orbit animation
orbit_anim = animator.create_orbit_animation(
    name="demo_orbit",
    center=np.array([0, 0, 0]),
    radius=20.0,
    height=5.0,
    duration=10.0,
    revolutions=2
)

# Play animation
animator.play_animation("demo_orbit", loop=True)

# Keyframe system
keyframes = plotx.KeyFrameSystem()
timeline_anim = keyframes.create_timeline_animation("complex_sequence")

# Add keyframes
position_track = timeline_anim.create_track("position")
position_track.add_keyframe(0.0, np.array([0, 0, 10]))
position_track.add_keyframe(5.0, np.array([10, 5, 10]))
position_track.add_keyframe(10.0, np.array([0, 10, 0]))

keyframes.play_timeline(loop=False)
```

## VR/AR Support

### VRRenderer

Virtual reality rendering system.

```python
class VRRenderer:
    """VR rendering for immersive headsets."""

    def __init__(self, device_type: VRDevice = VRDevice.GENERIC_OPENVR):
        """Initialize VR system."""

    def initialize(self) -> bool:
        """Initialize VR hardware."""

    def update_poses(self):
        """Update all device poses."""

    def render_frame(self, render_func: Callable[[Eye], None]):
        """Render VR frame for both eyes."""

    def get_hmd_pose(self) -> VRPose:
        """Get current HMD pose."""

    def get_controller(self, controller_id: int) -> Optional[VRController]:
        """Get controller by ID."""

    def vibrate_controller(self, controller_id: int,
                          intensity: float, duration: float):
        """Trigger haptic feedback."""
```

### ARRenderer

Augmented reality integration.

```python
class ARRenderer:
    """AR rendering for real-world overlay."""

    def __init__(self, device_type: ARDevice = ARDevice.ARCORE):
        """Initialize AR system."""

    def hit_test(self, screen_x: float, screen_y: float) -> Optional[VRPose]:
        """Test intersection with real world."""

    def create_anchor(self, pose: VRPose) -> str:
        """Create tracking anchor."""

    def get_detected_planes(self) -> List[Dict[str, Any]]:
        """Get detected plane surfaces."""
```

**Example Usage:**

```python
# VR setup
vr = plotx.VRRenderer(plotx.VRDevice.OCULUS_QUEST)
if vr.initialize():
    # Render loop
    def render_eye(eye):
        # Render 3D scene for this eye
        render_scene(eye.view_matrix, eye.projection_matrix)

    vr.render_frame(render_eye)

# AR setup
ar = plotx.ARRenderer(plotx.ARDevice.ARCORE)
if ar.initialize():
    # Place object in AR
    hit_result = ar.hit_test(screen_x=400, screen_y=300)
    if hit_result:
        anchor_id = ar.create_anchor(hit_result)
        place_virtual_object_at_anchor(anchor_id)
```

## Integration Examples

### Complete 3D Scene Setup

```python
import plotx
import numpy as np

# Create 3D scene
scene = plotx.Scene3D()

# Setup camera
camera = plotx.OrbitController(distance=15.0)
scene.set_camera(camera)

# Setup selection
selection = plotx.SelectionManager()
selection.set_selection_mode(plotx.SelectionMode.MULTIPLE)
scene.set_selection_manager(selection)

# Setup manipulation
manipulator = plotx.ObjectManipulator()
scene.set_manipulator(manipulator)

# Add objects
for i in range(10):
    obj = plotx.Cube(position=[i*2, 0, 0], scale=[1, 1, 1])
    scene.add_object(obj)

    # Make selectable and manipulatable
    selectable = plotx.SelectableObject(f"cube_{i}", obj.position, obj.bounds)
    selection.add_object(selectable)
    manipulator.add_object(f"cube_{i}", obj.transform)

# Setup gestures
gestures = plotx.GestureRecognizer(800, 600)
gestures.add_gesture_callback(plotx.GestureType.TAP, handle_selection)
gestures.add_gesture_callback(plotx.GestureType.DRAG, handle_camera_rotate)
gestures.add_gesture_callback(plotx.GestureType.PINCH, handle_camera_zoom)

# Run interactive session
scene.run()
```

---

This completes the 3D interaction API reference. For implementation examples and tutorials, see the [3D Examples](../examples/3d.md) section.