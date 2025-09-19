"""Advanced 3D interaction libraries for PlotX."""

from .camera import CameraController, OrbitController, FlyController, FirstPersonController
from .gestures import GestureRecognizer, TouchHandler, MouseHandler
from .selection import SelectionManager, RaycastSelector, BoxSelector
from .manipulation import Transform3D, ManipulatorGizmo, ObjectManipulator
from .navigation import NavigationController, PathPlanner, Waypoint
from .animation import CameraAnimator, ObjectAnimator, KeyFrameSystem
from .vr import VRRenderer, ARRenderer, SpatialController

__all__ = [
    # Camera controls
    "CameraController",
    "OrbitController",
    "FlyController",
    "FirstPersonController",

    # Gesture recognition
    "GestureRecognizer",
    "TouchHandler",
    "MouseHandler",

    # Selection systems
    "SelectionManager",
    "RaycastSelector",
    "BoxSelector",

    # Object manipulation
    "Transform3D",
    "ManipulatorGizmo",
    "ObjectManipulator",

    # Navigation
    "NavigationController",
    "PathPlanner",
    "Waypoint",

    # Animation
    "CameraAnimator",
    "ObjectAnimator",
    "KeyFrameSystem",

    # VR/AR support
    "VRRenderer",
    "ARRenderer",
    "SpatialController",
]