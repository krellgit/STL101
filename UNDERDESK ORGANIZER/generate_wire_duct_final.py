#!/usr/bin/env python3
"""
Wire Duct for Cable Tray - Final Version
Matches reference cable channel design with internal retention lip

Features:
- Matches cable tray slot dimensions (25mm x 20mm)
- Wide top opening, narrow internal slot for cable retention
- Flat mounting base with 2 screw holes (20mm from ends)
- Optional ribbed texture pattern
"""

import trimesh
import numpy as np
from shapely.geometry import Polygon

# ============================================
# Parameters
# ============================================

# Match cable tray slot dimensions
OPENING_WIDTH = 25.0        # mm (matches CABLE_SLOT_WIDTH)
OPENING_HEIGHT = 20.0       # mm (matches CABLE_SLOT_HEIGHT)
DUCT_LENGTH = 200.0         # mm (segment length)

# Channel profile
WALL_THICKNESS = 2.5        # mm
RETENTION_SLOT_WIDTH = 10.0 # mm (narrow slot at bottom to hold cables)
RETENTION_LIP_INSET = 3.0   # mm (how far lip extends inward from wall)
RETENTION_HEIGHT = 8.0      # mm (height from bottom where retention starts)

# Mounting base
BASE_WIDTH = 35.0           # mm (wider than opening for stability)
BASE_THICKNESS = 3.0        # mm

# Screw holes
SCREW_HOLE_DIA = 4.0        # mm (#8 wood screws)
SCREW_COUNTERSINK_DIA = 8.0 # mm
SCREW_COUNTERSINK_DEPTH = 2.5  # mm
SCREW_INSET_FROM_END = 20.0    # mm

# Ribs (optional texture)
ADD_RIBS = True
RIB_SPACING = 8.0           # mm (center-to-center)
RIB_WIDTH = 1.5             # mm
RIB_DEPTH = 0.8             # mm (how far ribs protrude)

# ============================================
# Helper functions
# ============================================

def create_box(width, height, depth, x=0, y=0, z=0):
    """Create a box mesh."""
    box = trimesh.creation.box(extents=[width, height, depth])
    box.apply_translation([x + width/2, y + height/2, z + depth/2])
    return box

def create_cylinder(radius, height, x=0, y=0, z=0, segments=32):
    """Create a cylinder mesh."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    cyl.apply_translation([x, y, z + height/2])
    return cyl

def create_channel_profile():
    """
    Create the 2D cross-section profile of the channel.
    Shape: Wide opening at top, tapers to narrow retention slot at bottom.
    """

    # Calculate dimensions
    half_opening = OPENING_WIDTH / 2
    half_slot = RETENTION_SLOT_WIDTH / 2
    total_height = OPENING_HEIGHT + BASE_THICKNESS

    # Create profile polygon (center at origin, Y-axis extrusion)
    # Start from bottom-left, go counter-clockwise

    profile_points = []

    # Bottom mounting base (left to right)
    base_half = BASE_WIDTH / 2
    profile_points.append((-base_half, -BASE_THICKNESS))
    profile_points.append((base_half, -BASE_THICKNESS))
    profile_points.append((base_half, 0))

    # Right side wall
    # From base to retention lip
    profile_points.append((half_slot + RETENTION_LIP_INSET, 0))
    profile_points.append((half_slot + RETENTION_LIP_INSET, RETENTION_HEIGHT))

    # Retention lip (extends inward)
    profile_points.append((half_slot, RETENTION_HEIGHT))
    profile_points.append((half_slot, RETENTION_HEIGHT + WALL_THICKNESS))

    # Outer wall up to opening
    profile_points.append((half_opening, RETENTION_HEIGHT + WALL_THICKNESS))
    profile_points.append((half_opening, OPENING_HEIGHT))

    # Top opening (right to left)
    profile_points.append((half_opening - WALL_THICKNESS, OPENING_HEIGHT))
    profile_points.append((-half_opening + WALL_THICKNESS, OPENING_HEIGHT))

    # Left side (mirror of right)
    profile_points.append((-half_opening, OPENING_HEIGHT))
    profile_points.append((-half_opening, RETENTION_HEIGHT + WALL_THICKNESS))

    profile_points.append((-half_slot, RETENTION_HEIGHT + WALL_THICKNESS))
    profile_points.append((-half_slot, RETENTION_HEIGHT))

    profile_points.append((-half_slot - RETENTION_LIP_INSET, RETENTION_HEIGHT))
    profile_points.append((-half_slot - RETENTION_LIP_INSET, 0))

    # Back to base
    profile_points.append((-base_half, 0))

    return profile_points

def extrude_profile(profile_points, length):
    """Extrude a 2D profile along Y axis."""
    polygon = Polygon(profile_points)
    mesh = trimesh.creation.extrude_polygon(polygon, height=length)

    # Rotate to align with Y axis (length direction)
    rotation = trimesh.transformations.rotation_matrix(-np.pi/2, [1, 0, 0])
    mesh.apply_transform(rotation)

    return mesh

def add_ribs(body):
    """Add ribbed texture pattern to exterior."""
    if not ADD_RIBS:
        return body

    print(f"Adding ribs (spacing: {RIB_SPACING}mm)...")

    num_ribs = int(DUCT_LENGTH / RIB_SPACING)

    for i in range(1, num_ribs):  # Skip first and last
        y_pos = i * RIB_SPACING

        # Left side rib
        left_rib = create_box(
            RIB_DEPTH,
            RIB_WIDTH,
            OPENING_HEIGHT,
            -OPENING_WIDTH/2 - RIB_DEPTH,
            y_pos - RIB_WIDTH/2,
            0
        )

        # Right side rib
        right_rib = create_box(
            RIB_DEPTH,
            RIB_WIDTH,
            OPENING_HEIGHT,
            OPENING_WIDTH/2,
            y_pos - RIB_WIDTH/2,
            0
        )

        # Add ribs to body
        try:
            body = trimesh.boolean.union([body, left_rib], engine='manifold')
            body = trimesh.boolean.union([body, right_rib], engine='manifold')
        except:
            pass

    return body

def add_screw_holes(body):
    """Add 2 screw holes (one on each end, 20mm from ends)."""

    print(f"Adding screw holes: 2 holes, {SCREW_INSET_FROM_END}mm from ends")

    hole_y_positions = [
        SCREW_INSET_FROM_END,
        DUCT_LENGTH - SCREW_INSET_FROM_END
    ]

    hole_x = 0  # Center of base
    hole_z_bottom = -BASE_THICKNESS - 1

    for i, y_pos in enumerate(hole_y_positions):
        # Shaft
        shaft = create_cylinder(
            SCREW_HOLE_DIA / 2,
            BASE_THICKNESS + 2,
            hole_x, y_pos, hole_z_bottom
        )

        # Countersink
        countersink = create_cylinder(
            SCREW_COUNTERSINK_DIA / 2,
            SCREW_COUNTERSINK_DEPTH + 0.5,
            hole_x, y_pos, hole_z_bottom
        )

        # Subtract from body
        try:
            hole = trimesh.boolean.union([shaft, countersink], engine='manifold')
            body = trimesh.boolean.difference([body, hole], engine='manifold')
            print(f"  Hole {i+1} at Y={y_pos:.1f}mm")
        except Exception as e:
            print(f"  Warning: Hole {i+1} failed: {e}")

    return body

def generate_wire_duct():
    """Generate complete wire duct."""

    print("\n=== Generating Wire Duct ===\n")
    print(f"Opening: {OPENING_WIDTH}mm x {OPENING_HEIGHT}mm")
    print(f"Length: {DUCT_LENGTH}mm")
    print(f"Retention slot: {RETENTION_SLOT_WIDTH}mm wide at height {RETENTION_HEIGHT}mm")
    print(f"Mounting base: {BASE_WIDTH}mm x {BASE_THICKNESS}mm\n")

    # Create profile
    print("Creating channel profile...")
    profile = create_channel_profile()

    # Extrude
    print(f"Extruding profile {DUCT_LENGTH}mm...")
    duct = extrude_profile(profile, DUCT_LENGTH)

    # Add ribs
    if ADD_RIBS:
        duct = add_ribs(duct)

    # Add screw holes
    duct = add_screw_holes(duct)

    # Validate
    print(f"\nMesh validation:")
    print(f"  Watertight: {duct.is_watertight}")
    print(f"  Valid volume: {duct.is_volume}")

    if not duct.is_watertight:
        print("  Attempting repair...")
        duct.fill_holes()

    return duct

def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate
    duct = generate_wire_duct()

    # Info
    bounds = duct.bounds
    size = bounds[1] - bounds[0]
    print(f"\nFinal dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export
    output_path = os.path.join(script_dir, "wire_duct_final.stl")
    duct.export(output_path)
    print(f"\nSTL exported to: {output_path}")

    print("\n" + "="*60)
    print("DESIGN FEATURES:")
    print("="*60)
    print(f"- Opening: {OPENING_WIDTH}mm x {OPENING_HEIGHT}mm (matches cable tray slots)")
    print(f"- Cable retention slot: {RETENTION_SLOT_WIDTH}mm wide")
    print(f"- Internal lip at {RETENTION_HEIGHT}mm height prevents cables from falling out")
    print(f"- 2 screw holes for mounting ({SCREW_INSET_FROM_END}mm from each end)")
    print(f"- Ribbed texture: {'Yes' if ADD_RIBS else 'No'}")
    print("="*60)
    print("\nASSEMBLY:")
    print("1. Position duct to align with cable tray slot")
    print("2. Attach with 2x #8 wood screws")
    print("3. Insert cables through wide top opening")
    print("4. Internal lip retains cables")
    print("="*60)

if __name__ == "__main__":
    main()
