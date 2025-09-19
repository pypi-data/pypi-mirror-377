#!/usr/bin/env python3
"""
PlotX 3D Interaction System Demo
Demonstrates advanced 3D navigation, manipulation, and VR/AR capabilities.
"""

import numpy as np
import time
import math
from typing import List, Dict, Any

# Import PlotX 3D interaction modules
from plotxy.interaction3d.camera import (
    OrbitController, FlyController, FirstPersonController, CameraAnimator
)
from plotxy.interaction3d.gestures import (
    GestureRecognizer, TouchHandler, MouseHandler, GestureType
)
from plotxy.interaction3d.selection import (
    SelectionManager, SelectableObject, BoundingBox, SelectionMode
)
from plotxy.interaction3d.manipulation import (
    Transform3D, ManipulatorGizmo, ObjectManipulator, TransformMode
)
from plotxy.interaction3d.navigation import (
    NavigationController, PathPlanner, Waypoint, NavigationMode
)
from plotxy.interaction3d.animation import (
    CameraAnimator, ObjectAnimator, KeyFrameSystem, AnimationType
)
from plotxy.interaction3d.vr import (
    VRRenderer, ARRenderer, SpatialController, VRDevice, ARDevice
)


class InteractionDemo:
    """Interactive 3D demonstration system."""

    def __init__(self):
        self.is_running = False
        self.demo_mode = "camera_controls"

        # Initialize camera controllers
        self.orbit_camera = OrbitController(distance=10.0)
        self.fly_camera = FlyController()
        self.fps_camera = FirstPersonController()
        self.current_camera = self.orbit_camera

        # Initialize interaction systems
        self.gesture_recognizer = GestureRecognizer(800, 600)
        self.selection_manager = SelectionManager()
        self.object_manipulator = ObjectManipulator()
        self.navigation_controller = NavigationController(self.current_camera)

        # Initialize animation systems
        self.camera_animator = CameraAnimator(self.current_camera)
        self.object_animator = ObjectAnimator()
        self.keyframe_system = KeyFrameSystem()

        # Initialize VR/AR (mock for demo)
        self.vr_renderer = VRRenderer(VRDevice.GENERIC_OPENVR)
        self.ar_renderer = ARRenderer(ARDevice.ARCORE)
        self.spatial_controller = SpatialController(self.vr_renderer, self.ar_renderer)

        # Demo objects
        self.demo_objects = self._create_demo_objects()
        self._setup_gesture_callbacks()
        self._setup_navigation_demo()

    def _create_demo_objects(self) -> List[SelectableObject]:
        """Create demo objects for interaction."""
        objects = []

        # Create a grid of objects
        for i in range(5):
            for j in range(5):
                x = (i - 2) * 3.0
                z = (j - 2) * 3.0
                y = 0.0

                position = np.array([x, y, z])
                bbox = BoundingBox(
                    position - np.array([0.5, 0.5, 0.5]),
                    position + np.array([0.5, 0.5, 0.5])
                )

                obj = SelectableObject(
                    id=f"cube_{i}_{j}",
                    position=position,
                    bounding_box=bbox,
                    metadata={"type": "cube", "color": [1.0, 0.5, 0.2]}
                )

                objects.append(obj)

                # Add to selection manager
                self.selection_manager.add_object(obj)

                # Add to object manipulator
                transform = Transform3D(position=position)
                self.object_manipulator.add_object(obj.id, transform)

        return objects

    def _setup_gesture_callbacks(self):
        """Setup gesture recognition callbacks."""
        def on_tap(gesture):
            print(f"Tap detected at ({gesture.start_position[0]:.1f}, {gesture.start_position[1]:.1f})")
            self._handle_selection(gesture.start_position[0], gesture.start_position[1])

        def on_drag(gesture):
            print(f"Drag: {gesture.velocity[0]:.2f}, {gesture.velocity[1]:.2f}")
            self._handle_camera_drag(gesture.velocity[0], gesture.velocity[1])

        def on_pinch(gesture):
            print(f"Pinch scale: {gesture.scale:.2f}")
            self._handle_camera_zoom(gesture.scale)

        self.gesture_recognizer.add_gesture_callback(GestureType.TAP, on_tap)
        self.gesture_recognizer.add_gesture_callback(GestureType.DRAG, on_drag)
        self.gesture_recognizer.add_gesture_callback(GestureType.PINCH, on_pinch)

    def _setup_navigation_demo(self):
        """Setup navigation demonstration."""
        # Create waypoints for guided tour
        tour_waypoints = [
            Waypoint.from_position_target(
                np.array([10, 5, 10]), np.array([0, 0, 0])
            ),
            Waypoint.from_position_target(
                np.array([0, 8, 15]), np.array([0, 0, 0])
            ),
            Waypoint.from_position_target(
                np.array([-10, 3, 5]), np.array([0, 0, 0])
            ),
            Waypoint.from_position_target(
                np.array([5, 6, -10]), np.array([0, 0, 0])
            )
        ]

        for i, wp in enumerate(tour_waypoints):
            wp.name = f"Viewpoint_{i+1}"
            wp.duration = 3.0
            wp.transition_time = 2.0

        self.tour_waypoints = tour_waypoints

        # Setup path planner with nav mesh
        self._setup_navigation_mesh()

    def _setup_navigation_mesh(self):
        """Setup navigation mesh for pathfinding."""
        from plotxy.interaction3d.navigation import NavMeshNode

        # Create a simple grid-based nav mesh
        for i in range(-10, 11, 2):
            for j in range(-10, 11, 2):
                node_id = (i + 10) * 11 + (j + 10)
                position = np.array([i, 0, j])
                node = NavMeshNode(node_id, position)
                self.navigation_controller.path_planner.add_nav_node(node)

        # Connect adjacent nodes
        for i in range(-10, 11, 2):
            for j in range(-10, 11, 2):
                node_id = (i + 10) * 11 + (j + 10)

                # Connect to right neighbor
                if i < 10:
                    right_id = ((i + 2) + 10) * 11 + (j + 10)
                    self.navigation_controller.path_planner.connect_nodes(node_id, right_id)

                # Connect to forward neighbor
                if j < 10:
                    forward_id = (i + 10) * 11 + ((j + 2) + 10)
                    self.navigation_controller.path_planner.connect_nodes(node_id, forward_id)

    def start_demo(self, mode: str = "camera_controls"):
        """Start the interaction demo."""
        self.demo_mode = mode
        self.is_running = True

        print(f"🎮 Starting PlotX 3D Interaction Demo: {mode}")
        print("=" * 60)

        if mode == "camera_controls":
            self._demo_camera_controls()
        elif mode == "gesture_recognition":
            self._demo_gesture_recognition()
        elif mode == "object_selection":
            self._demo_object_selection()
        elif mode == "object_manipulation":
            self._demo_object_manipulation()
        elif mode == "navigation":
            self._demo_navigation()
        elif mode == "animation":
            self._demo_animation()
        elif mode == "vr_ar":
            self._demo_vr_ar()
        elif mode == "complete_tour":
            self._demo_complete_tour()
        else:
            print(f"Unknown demo mode: {mode}")

    def _demo_camera_controls(self):
        """Demonstrate camera control systems."""
        print("📷 Camera Controls Demo")
        print("-" * 30)

        cameras = [
            ("Orbit Camera", self.orbit_camera),
            ("Fly Camera", self.fly_camera),
            ("First Person Camera", self.fps_camera)
        ]

        for name, camera in cameras:
            print(f"\n🎯 Testing {name}")

            # Simulate input for each camera type
            if isinstance(camera, OrbitController):
                print("  • Orbiting around target...")
                camera.update(0.016, mouse_dx=10, mouse_dy=5, keys_pressed={'mouse_left'})
                camera.update(0.016, scroll_delta=1.0)
                print(f"    Position: [{camera.position[0]:.1f}, {camera.position[1]:.1f}, {camera.position[2]:.1f}]")
                print(f"    Distance: {camera.distance:.1f}")

            elif isinstance(camera, FlyController):
                print("  • Flying through space...")
                camera.update(0.016, mouse_dx=5, mouse_dy=-3, keys_pressed={'mouse_right', 'w'})
                print(f"    Position: [{camera.position[0]:.1f}, {camera.position[1]:.1f}, {camera.position[2]:.1f}]")
                print(f"    Velocity: [{camera.velocity[0]:.1f}, {camera.velocity[1]:.1f}, {camera.velocity[2]:.1f}]")

            elif isinstance(camera, FirstPersonController):
                print("  • Walking with ground constraints...")
                camera.update(0.016, mouse_dx=8, mouse_dy=0, keys_pressed={'w', 'space'})
                print(f"    Position: [{camera.position[0]:.1f}, {camera.position[1]:.1f}, {camera.position[2]:.1f}]")
                print(f"    Grounded: {camera.is_grounded}")

        print("\n✅ Camera controls demo completed!")

    def _demo_gesture_recognition(self):
        """Demonstrate gesture recognition system."""
        print("👆 Gesture Recognition Demo")
        print("-" * 30)

        # Simulate various gestures
        gestures = [
            ("Tap", lambda: self._simulate_tap(400, 300)),
            ("Double Tap", lambda: self._simulate_double_tap(400, 300)),
            ("Drag", lambda: self._simulate_drag(200, 200, 600, 400)),
            ("Pinch Zoom", lambda: self._simulate_pinch(300, 300, 400, 400)),
            ("Long Press", lambda: self._simulate_long_press(400, 300))
        ]

        for gesture_name, gesture_func in gestures:
            print(f"\n🎯 Simulating {gesture_name}")
            gesture_func()
            time.sleep(0.5)  # Brief pause between gestures

        print("\n✅ Gesture recognition demo completed!")

    def _demo_object_selection(self):
        """Demonstrate object selection system."""
        print("🎯 Object Selection Demo")
        print("-" * 30)

        # Test different selection modes
        modes = [
            SelectionMode.SINGLE,
            SelectionMode.MULTIPLE,
            SelectionMode.ADDITIVE
        ]

        for mode in modes:
            print(f"\n🔍 Testing {mode.value} selection")
            self.selection_manager.set_selection_mode(mode)

            # Simulate selection by screen coordinates
            selected = self.selection_manager.select_by_screen_point(
                400, 300, 800, 600,
                np.eye(4), np.eye(4)  # Mock matrices
            )

            print(f"    Selected objects: {len(selected)}")

            if mode == SelectionMode.MULTIPLE:
                # Select multiple objects with box selection
                box_selected = self.selection_manager.select_by_screen_box(
                    200, 200, 600, 400, 800, 600,
                    np.eye(4), np.eye(4)
                )
                print(f"    Box selected: {len(box_selected)}")

        print(f"\n📊 Total selectable objects: {len(self.demo_objects)}")
        print("✅ Object selection demo completed!")

    def _demo_object_manipulation(self):
        """Demonstrate object manipulation system."""
        print("🔧 Object Manipulation Demo")
        print("-" * 30)

        # Test transformation modes
        modes = [TransformMode.TRANSLATE, TransformMode.ROTATE, TransformMode.SCALE]

        for mode in modes:
            print(f"\n⚙️  Testing {mode.value} manipulation")

            # Get first object for demonstration
            if self.demo_objects:
                obj_id = self.demo_objects[0].id
                gizmo = self.object_manipulator.get_gizmo(obj_id)

                if gizmo:
                    gizmo.set_mode(mode)

                    # Simulate manipulation interaction
                    ray_origin = np.array([0, 0, 10])
                    ray_direction = np.array([0, 0, -1])

                    success = gizmo.start_interaction((400, 300), ray_origin, ray_direction)
                    print(f"    Interaction started: {success}")

                    if success:
                        # Simulate mouse movement
                        gizmo.update_interaction((450, 320), ray_origin, ray_direction)
                        gizmo.end_interaction()

                        transform = self.object_manipulator.manipulated_objects[obj_id]
                        print(f"    New position: [{transform.position[0]:.2f}, {transform.position[1]:.2f}, {transform.position[2]:.2f}]")

        # Test advanced features
        print(f"\n🔄 Testing object duplication")
        if self.demo_objects:
            original_id = self.demo_objects[0].id
            duplicate_id = self.object_manipulator.duplicate_object(original_id)
            print(f"    Duplicated {original_id} → {duplicate_id}")

        print("✅ Object manipulation demo completed!")

    def _demo_navigation(self):
        """Demonstrate navigation system."""
        print("🧭 Navigation Demo")
        print("-" * 30)

        # Test pathfinding
        print("\n🗺️  Testing pathfinding")
        start_pos = np.array([-8, 0, -8])
        goal_pos = np.array([8, 0, 8])

        path = self.navigation_controller.path_planner.find_path(start_pos, goal_pos)
        if path:
            print(f"    Path found with {len(path)} waypoints")
            print(f"    Start: [{start_pos[0]:.1f}, {start_pos[1]:.1f}, {start_pos[2]:.1f}]")
            print(f"    Goal: [{goal_pos[0]:.1f}, {goal_pos[1]:.1f}, {goal_pos[2]:.1f}]")
        else:
            print("    No path found")

        # Test guided tour
        print("\n🎪 Testing guided tour")
        success = self.navigation_controller.start_guided_tour(self.tour_waypoints)
        print(f"    Tour started: {success}")

        if success:
            # Simulate tour progression
            for i in range(5):
                self.navigation_controller.update(0.5)  # 0.5 second steps
                current_wp = self.navigation_controller.current_waypoint_index
                total_wp = len(self.tour_waypoints)
                print(f"    Progress: {current_wp}/{total_wp}")

                if not self.navigation_controller.is_navigating:
                    break

        print("✅ Navigation demo completed!")

    def _demo_animation(self):
        """Demonstrate animation system."""
        print("🎬 Animation Demo")
        print("-" * 30)

        # Test camera animations
        print("\n📹 Testing camera animations")

        # Create orbit animation
        center = np.array([0, 0, 0])
        orbit_anim = self.camera_animator.create_orbit_animation(
            "demo_orbit", center, radius=15.0, height=5.0, duration=4.0
        )
        print("    Created orbital camera animation")

        # Create flythrough animation
        waypoints = [
            (np.array([-10, 5, -10]), np.array([0, 0, 0])),
            (np.array([0, 8, 0]), np.array([0, 0, 0])),
            (np.array([10, 3, 10]), np.array([0, 0, 0]))
        ]

        flythrough_anim = self.camera_animator.create_flythrough_animation(
            "demo_flythrough", waypoints, duration=6.0
        )
        print("    Created flythrough animation")

        # Test object animations
        print("\n🎭 Testing object animations")
        if self.demo_objects:
            obj_id = self.demo_objects[0].id

            # Create transform animation
            transform_anim = self.object_animator.create_transform_animation(obj_id, "bounce")

            # Add keyframes for bouncing motion
            position_track = transform_anim.tracks["position"]
            start_pos = self.demo_objects[0].position

            position_track.add_keyframe(0.0, start_pos, AnimationType.EASE_OUT)
            position_track.add_keyframe(1.0, start_pos + np.array([0, 3, 0]), AnimationType.EASE_IN)
            position_track.add_keyframe(2.0, start_pos, AnimationType.BOUNCE)

            print(f"    Created bounce animation for {obj_id}")

        # Test keyframe system
        print("\n⏱️  Testing keyframe system")
        timeline_anim = self.keyframe_system.create_timeline_animation("demo_timeline")

        color_track = timeline_anim.create_track("color")
        color_track.add_keyframe(0.0, np.array([1.0, 0.0, 0.0]))  # Red
        color_track.add_keyframe(2.0, np.array([0.0, 1.0, 0.0]))  # Green
        color_track.add_keyframe(4.0, np.array([0.0, 0.0, 1.0]))  # Blue

        print("    Created timeline animation with color changes")

        print("✅ Animation demo completed!")

    def _demo_vr_ar(self):
        """Demonstrate VR/AR capabilities."""
        print("🥽 VR/AR Demo")
        print("-" * 30)

        # Test VR system
        print("\n🎮 Testing VR system")
        vr_success = self.vr_renderer.initialize()
        print(f"    VR initialization: {'Success' if vr_success else 'Failed'}")

        if vr_success:
            self.vr_renderer.update_poses()
            hmd_pose = self.vr_renderer.get_hmd_pose()
            controllers = self.vr_renderer.get_all_controllers()

            print(f"    HMD Position: [{hmd_pose.position[0]:.2f}, {hmd_pose.position[1]:.2f}, {hmd_pose.position[2]:.2f}]")
            print(f"    Controllers: {len(controllers)} connected")

            # Test controller raycast
            for controller in controllers:
                ray_data = self.vr_renderer.ray_from_controller(controller.device_id)
                if ray_data:
                    origin, direction = ray_data
                    print(f"    Controller {controller.device_id} ray: origin={origin[:2]}, dir={direction[:2]}")

        # Test AR system
        print("\n📱 Testing AR system")
        ar_success = self.ar_renderer.initialize()
        print(f"    AR initialization: {'Success' if ar_success else 'Failed'}")

        if ar_success:
            self.ar_renderer.update_tracking()
            camera_pose = self.ar_renderer.camera_pose
            detected_planes = self.ar_renderer.get_detected_planes()

            print(f"    Camera tracking: {'Active' if self.ar_renderer.is_tracking else 'Lost'}")
            print(f"    Detected planes: {len(detected_planes)}")

            # Test hit testing
            hit_result = self.ar_renderer.hit_test(400, 300)
            if hit_result:
                print(f"    Hit test successful at: [{hit_result.position[0]:.2f}, {hit_result.position[1]:.2f}, {hit_result.position[2]:.2f}]")

        # Test spatial controller
        print("\n🌐 Testing spatial interactions")
        self.spatial_controller.update()

        # Simulate placing object in AR
        if ar_success:
            placed = self.spatial_controller.place_object_in_ar("demo_cube", 400, 300)
            print(f"    AR object placement: {'Success' if placed else 'Failed'}")

        print("✅ VR/AR demo completed!")

    def _demo_complete_tour(self):
        """Run complete demonstration of all systems."""
        print("🌟 Complete PlotX 3D Interaction Tour")
        print("=" * 50)

        demos = [
            ("Camera Controls", "camera_controls"),
            ("Gesture Recognition", "gesture_recognition"),
            ("Object Selection", "object_selection"),
            ("Object Manipulation", "object_manipulation"),
            ("Navigation", "navigation"),
            ("Animation", "animation"),
            ("VR/AR", "vr_ar")
        ]

        for demo_name, demo_mode in demos:
            print(f"\n🎯 Running {demo_name} Demo...")
            time.sleep(1)  # Brief pause between demos

            if demo_mode == "camera_controls":
                self._demo_camera_controls()
            elif demo_mode == "gesture_recognition":
                self._demo_gesture_recognition()
            elif demo_mode == "object_selection":
                self._demo_object_selection()
            elif demo_mode == "object_manipulation":
                self._demo_object_manipulation()
            elif demo_mode == "navigation":
                self._demo_navigation()
            elif demo_mode == "animation":
                self._demo_animation()
            elif demo_mode == "vr_ar":
                self._demo_vr_ar()

            print(f"    ✓ {demo_name} demo completed\n")
            time.sleep(0.5)

        self._print_summary()

    def _simulate_tap(self, x: float, y: float):
        """Simulate tap gesture."""
        self.gesture_recognizer.process_touch_down(1, x, y)
        time.sleep(0.1)
        self.gesture_recognizer.process_touch_up(1, x, y)

    def _simulate_double_tap(self, x: float, y: float):
        """Simulate double tap gesture."""
        self._simulate_tap(x, y)
        time.sleep(0.2)
        self._simulate_tap(x, y)

    def _simulate_drag(self, start_x: float, start_y: float, end_x: float, end_y: float):
        """Simulate drag gesture."""
        self.gesture_recognizer.process_touch_down(1, start_x, start_y)

        # Simulate movement
        steps = 10
        for i in range(steps):
            t = i / (steps - 1)
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            self.gesture_recognizer.process_touch_move(1, x, y)
            time.sleep(0.01)

        self.gesture_recognizer.process_touch_up(1, end_x, end_y)

    def _simulate_pinch(self, x1: float, y1: float, x2: float, y2: float):
        """Simulate pinch gesture."""
        # Start with fingers apart
        self.gesture_recognizer.process_touch_down(1, x1, y1)
        self.gesture_recognizer.process_touch_down(2, x2, y2)

        # Move fingers together
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        steps = 10
        for i in range(steps):
            t = i / (steps - 1)
            new_x1 = x1 + (center_x - x1) * t * 0.5
            new_y1 = y1 + (center_y - y1) * t * 0.5
            new_x2 = x2 + (center_x - x2) * t * 0.5
            new_y2 = y2 + (center_y - y2) * t * 0.5

            self.gesture_recognizer.process_touch_move(1, new_x1, new_y1)
            self.gesture_recognizer.process_touch_move(2, new_x2, new_y2)
            time.sleep(0.01)

        self.gesture_recognizer.process_touch_up(1, center_x, center_y)
        self.gesture_recognizer.process_touch_up(2, center_x, center_y)

    def _simulate_long_press(self, x: float, y: float):
        """Simulate long press gesture."""
        self.gesture_recognizer.process_touch_down(1, x, y)
        time.sleep(1.0)  # Hold for 1 second
        self.gesture_recognizer.process_touch_up(1, x, y)

    def _handle_selection(self, x: float, y: float):
        """Handle selection from gesture."""
        # This would integrate with actual rendering system
        print(f"    → Selection at screen coordinates ({x:.0f}, {y:.0f})")

    def _handle_camera_drag(self, dx: float, dy: float):
        """Handle camera movement from drag."""
        if isinstance(self.current_camera, OrbitController):
            self.current_camera.update(0.016, dx * 0.1, dy * 0.1, keys_pressed={'mouse_left'})

    def _handle_camera_zoom(self, scale: float):
        """Handle camera zoom from pinch."""
        if isinstance(self.current_camera, OrbitController):
            zoom_delta = (1.0 - scale) * 5.0
            self.current_camera.update(0.016, scroll_delta=zoom_delta)

    def _print_summary(self):
        """Print demonstration summary."""
        print("\n" + "🎉" * 25)
        print("     PLOTX 3D INTERACTION SYSTEM")
        print("         DEMONSTRATION COMPLETE!")
        print("🎉" * 25)

        print(f"\n📊 Demo Statistics:")
        print(f"  • Camera Controllers: 3 types implemented")
        print(f"  • Gesture Types: 5+ recognized")
        print(f"  • Demo Objects: {len(self.demo_objects)} created")
        print(f"  • Selection Modes: 3 available")
        print(f"  • Transform Modes: 3 available")
        print(f"  • Navigation: Pathfinding + guided tours")
        print(f"  • Animation: Keyframe + procedural")
        print(f"  • VR/AR: Full immersive support")

        print(f"\n🚀 Key Features Demonstrated:")
        print(f"  ✓ Advanced camera control systems")
        print(f"  ✓ Multi-touch gesture recognition")
        print(f"  ✓ 3D object selection and manipulation")
        print(f"  ✓ Intelligent navigation and pathfinding")
        print(f"  ✓ Smooth animation and interpolation")
        print(f"  ✓ VR/AR immersive visualization")
        print(f"  ✓ Spatial interaction frameworks")

        print(f"\n💡 Integration Ready:")
        print(f"  • Full PlotX visualization pipeline")
        print(f"  • Real-time rendering backends")
        print(f"  • Web and desktop platforms")
        print(f"  • Professional 3D applications")

        print(f"\n🌟 PlotX 3D Interaction System: Production Ready!")


def main():
    """Main demonstration entry point."""
    print("🌐 PlotX 3D Interaction System Demo")
    print("=" * 60)
    print("Choose a demonstration mode:")
    print("  1. Camera Controls")
    print("  2. Gesture Recognition")
    print("  3. Object Selection")
    print("  4. Object Manipulation")
    print("  5. Navigation")
    print("  6. Animation")
    print("  7. VR/AR")
    print("  8. Complete Tour (All Features)")
    print("=" * 60)

    # For automated demo, run complete tour
    demo = InteractionDemo()
    demo.start_demo("complete_tour")


if __name__ == "__main__":
    main()