#!/usr/bin/env python3
"""
Wire Duct for Cable Tray
Generates STL file for 3D printing

Features:
- Tube matches cable tray slot dimensions (25mm x 20mm)
- Snap-fit mounting clips that attach to desk edge or flat surface
- Modular design - print multiple segments for longer runs
"""

import trimesh
import numpy as np

# ============================================
# Parameters - adjust as needed
# ============================================

# Duct dimensions - match cable tray slot
DUCT_WIDTH = 25.0           # mm (matches CABLE_SLOT_WIDTH)
DUCT_HEIGHT = 20.0          # mm (matches CABLE_SLOT_HEIGHT)
DUCT_LENGTH = 150.0         # mm (segment length - print multiple for longer runs)
WALL_THICKNESS = 2.0        # mm (duct wall thickness)

# Cable opening (slot at bottom)
CABLE_OPENING_WIDTH = 8.0   # mm (slot for cables to enter/exit)

# Mounting clip parameters
CLIP_SPACING = 75.0         # mm (center-to-center distance between clips)
CLIP_WIDTH = 15.0           # mm (width of mounting clip)
CLIP_THICKNESS = 3.0        # mm (thickness of clip base)
CLIP_HEIGHT = 12.0          # mm (height of clip arm)
CLIP_LIP = 5.0              # mm (desk edge grip lip length)
CLIP_GAP = 20.0             # mm (desk thickness - adjust to fit)

# Corner radius for smooth edges
CORNER_RADIUS = 2.0         # mm

# ============================================
# Helper functions
# ============================================

def create_box(width, height, depth, x=0, y=0, z=0):
    """Create a box mesh at the specified position."""
    box = trimesh.creation.box(extents=[width, height, depth])
    box.apply_translation([x + width/2, y + height/2, z + depth/2])
    return box

def create_cylinder(radius, height, x=0, y=0, z=0, segments=32):
    """Create a cylinder mesh at the specified position."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    cyl.apply_translation([x, y, z + height/2])
    return cyl

def create_rounded_box(width, length, height, radius, x=0, y=0, z=0):
    """Create a box with rounded edges using cylinders at corners."""
    # Main body (reduced by corner radius on all sides)
    center_width = width - 2 * radius
    center_length = length - 2 * radius

    parts = []

    # Center box
    if center_width > 0 and center_length > 0:
        center = create_box(center_width, center_length, height,
                           x + radius, y + radius, z)
        parts.append(center)

    # Edge boxes
    if center_width > 0:
        # Top and bottom edges
        top_edge = create_box(center_width, 2*radius, height,
                             x + radius, y + length - radius, z)
        bottom_edge = create_box(center_width, 2*radius, height,
                                x + radius, y, z)
        parts.extend([top_edge, bottom_edge])

    if center_length > 0:
        # Left and right edges
        left_edge = create_box(2*radius, center_length, height,
                              x, y + radius, z)
        right_edge = create_box(2*radius, center_length, height,
                               x + width - radius, y + radius, z)
        parts.extend([left_edge, right_edge])

    # Corner cylinders (vertical)
    corners = [
        (x + radius, y + radius),
        (x + width - radius, y + radius),
        (x + width - radius, y + length - radius),
        (x + radius, y + length - radius),
    ]

    for cx, cy in corners:
        corner = create_cylinder(radius, height, cx, cy, z)
        parts.append(corner)

    # Union all parts
    result = parts[0]
    for part in parts[1:]:
        try:
            result = trimesh.boolean.union([result, part], engine='manifold')
        except:
            result = trimesh.util.concatenate([result, part])

    return result

# ============================================
# Main generation functions
# ============================================

def generate_duct_body():
    """Generate the main wire duct tube."""

    print(f"=== Wire Duct Tube ===")
    print(f"Outer: {DUCT_WIDTH}mm W x {DUCT_HEIGHT}mm H x {DUCT_LENGTH}mm L")
    print(f"Inner: {DUCT_WIDTH - 2*WALL_THICKNESS}mm W x {DUCT_HEIGHT - WALL_THICKNESS}mm H")
    print(f"Cable opening: {CABLE_OPENING_WIDTH}mm wide slot at bottom")

    # Outer shell
    outer = create_rounded_box(
        DUCT_WIDTH,
        DUCT_LENGTH,
        DUCT_HEIGHT,
        CORNER_RADIUS,
        0, 0, 0
    )

    # Inner cavity (U-shaped - open at bottom)
    inner_width = DUCT_WIDTH - 2 * WALL_THICKNESS
    inner_height = DUCT_HEIGHT  # Open at bottom
    inner_length = DUCT_LENGTH + 2  # Extra to ensure clean cut

    inner = create_box(
        inner_width,
        inner_length,
        inner_height,
        WALL_THICKNESS,
        -1,
        WALL_THICKNESS
    )

    # Subtract inner cavity
    print("Creating U-shaped tube...")
    try:
        shell = trimesh.boolean.difference([outer, inner], engine='manifold')
    except Exception as e:
        print(f"Boolean failed: {e}")
        shell = outer

    # Create cable entry slot at bottom (narrow opening)
    slot = create_box(
        CABLE_OPENING_WIDTH,
        DUCT_LENGTH + 2,
        WALL_THICKNESS + 1,
        (DUCT_WIDTH - CABLE_OPENING_WIDTH) / 2,
        -1,
        -0.5
    )

    # Subtract slot
    try:
        shell = trimesh.boolean.difference([shell, slot], engine='manifold')
    except Exception as e:
        print(f"Slot subtraction failed: {e}")

    return shell

def generate_mounting_clip(x_pos, y_pos):
    """Generate a single desk-edge mounting clip at the specified position."""

    # C-shaped clip that grabs desk edge
    # Structure: vertical arm up from duct, horizontal lip over desk top, vertical arm down back side

    parts = []

    # Base attachment to duct (on top surface)
    base = create_box(
        CLIP_WIDTH,
        CLIP_WIDTH,
        CLIP_THICKNESS,
        x_pos - CLIP_WIDTH/2,
        y_pos - CLIP_WIDTH/2,
        DUCT_HEIGHT  # Sits on top of duct
    )
    parts.append(base)

    # Vertical arm going up
    arm_up = create_box(
        CLIP_WIDTH,
        CLIP_THICKNESS,
        CLIP_HEIGHT,
        x_pos - CLIP_WIDTH/2,
        y_pos - CLIP_THICKNESS/2,
        DUCT_HEIGHT + CLIP_THICKNESS
    )
    parts.append(arm_up)

    # Horizontal lip (grabs desk top)
    lip = create_box(
        CLIP_WIDTH,
        CLIP_LIP,
        CLIP_THICKNESS,
        x_pos - CLIP_WIDTH/2,
        y_pos - CLIP_THICKNESS/2,
        DUCT_HEIGHT + CLIP_THICKNESS + CLIP_HEIGHT
    )
    parts.append(lip)

    # Vertical arm going down (back side of desk)
    arm_down = create_box(
        CLIP_WIDTH,
        CLIP_THICKNESS,
        CLIP_GAP,
        x_pos - CLIP_WIDTH/2,
        y_pos + CLIP_LIP - CLIP_THICKNESS/2,
        DUCT_HEIGHT + CLIP_THICKNESS + CLIP_HEIGHT - CLIP_GAP
    )
    parts.append(arm_down)

    # Back lip (hooks under desk)
    back_lip = create_box(
        CLIP_WIDTH,
        CLIP_LIP,
        CLIP_THICKNESS,
        x_pos - CLIP_WIDTH/2,
        y_pos + CLIP_LIP - CLIP_THICKNESS/2,
        DUCT_HEIGHT + CLIP_THICKNESS + CLIP_HEIGHT - CLIP_GAP - CLIP_THICKNESS
    )
    parts.append(back_lip)

    # Combine all clip parts
    clip = parts[0]
    for part in parts[1:]:
        try:
            clip = trimesh.boolean.union([clip, part], engine='manifold')
        except:
            clip = trimesh.util.concatenate([clip, part])

    return clip

def generate_wire_duct():
    """Generate complete wire duct with mounting clips."""

    print("\n=== Generating Wire Duct with Mounting Clips ===\n")

    # Generate main duct body
    duct = generate_duct_body()

    # Generate mounting clips at intervals
    num_clips = max(2, int(DUCT_LENGTH / CLIP_SPACING) + 1)
    clip_positions = np.linspace(CLIP_SPACING/2, DUCT_LENGTH - CLIP_SPACING/2, num_clips)

    print(f"\nAdding {num_clips} mounting clips...")

    clips = []
    for y_pos in clip_positions:
        # Center clip on duct width
        x_pos = DUCT_WIDTH / 2
        clip = generate_mounting_clip(x_pos, y_pos)
        clips.append(clip)

    # Combine duct with all clips
    print("Combining duct and clips...")
    result = duct
    for i, clip in enumerate(clips):
        try:
            result = trimesh.boolean.union([result, clip], engine='manifold')
        except Exception as e:
            print(f"Warning: Clip {i} union failed, using concatenate")
            result = trimesh.util.concatenate([result, clip])

    # Validate mesh
    print(f"\nMesh is watertight: {result.is_watertight}")
    print(f"Mesh is valid volume: {result.is_volume}")

    if not result.is_watertight:
        print("Attempting mesh repair...")
        result.fill_holes()

    return result

def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate the wire duct
    duct = generate_wire_duct()

    # Get bounds for info
    bounds = duct.bounds
    size = bounds[1] - bounds[0]
    print(f"\nWire duct dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export STL
    output_path = os.path.join(script_dir, "wire_duct.stl")
    duct.export(output_path)
    print(f"STL exported to: {output_path}")

    print("\n" + "="*50)
    print("ASSEMBLY INSTRUCTIONS:")
    print("="*50)
    print("1. Print wire_duct.stl (print multiple for longer runs)")
    print("2. Clips slide over desk edge (adjust CLIP_GAP for desk thickness)")
    print("3. Duct aligns with cable tray slot openings")
    print("4. Route cables through duct slot opening at bottom")
    print("5. Connect multiple segments end-to-end as needed")
    print("="*50)
    print(f"\nNOTE: Desk thickness set to {CLIP_GAP}mm")
    print("      Adjust CLIP_GAP parameter if your desk is different")

if __name__ == "__main__":
    main()
