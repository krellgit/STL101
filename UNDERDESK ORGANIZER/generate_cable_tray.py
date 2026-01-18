#!/usr/bin/env python3
"""
Enclosed Under-Desk Cable Tray with Ribbed Texture
Generates STL file for 3D printing

Features:
- Fully enclosed trough with front/back openings only
- Ribbed/fluted horizontal texture on exterior
- TROTTEN rail clip mounting system
"""

import trimesh
import numpy as np

# ============================================
# Parameters - adjust as needed
# ============================================

# Main tray dimensions
TRAY_LENGTH = 200.0      # mm (along desk, front-to-back openings)
TRAY_WIDTH = 120.0       # mm (side to side)
TRAY_DEPTH = 55.0        # mm (height/depth of tray cavity)

# Wall thickness - matches T-neck width so they print as one piece
WALL_THICKNESS = 3.0     # mm (same as RAIL_NECK_WIDTH)
BOTTOM_THICKNESS = 2.0   # mm (bottom thickness)

# Ribbed texture settings
RIB_SPACING = 4.0        # mm (center-to-center distance between ribs)
RIB_DEPTH = 1.2          # mm (how far ribs protrude)
RIB_WIDTH = 2.0          # mm (width of each rib)

# Corner radius
CORNER_RADIUS = 3.0      # mm (rounded corners on tray)

# T-slot slide-in mounting system
# Rail dimensions (T-shape: narrow neck + chamfered head) - full length design
RAIL_NECK_WIDTH = 3.0        # mm (narrow part - matches wall thickness)
RAIL_NECK_HEIGHT = 4.0       # mm (height of neck - increased for tolerance)
RAIL_HEAD_WIDTH = 10.0       # mm (wide part that gets captured at top)
RAIL_CHAMFER_HEIGHT = 3.0    # mm (45° chamfer from neck to head width)
RAIL_HEAD_FLAT = 0.5         # mm (flat top portion of head)
# T-profiles now run the full length of the tray for better load distribution
# Head is trapezoidal: starts at neck width, chamfers out to head width at 45°

# Rail frame (single piece that mounts to desk)
# Frame dimensions - calculated to match tray T-profile positions
# T-profiles are centered on tray walls at: x = WALL_THICKNESS/2 and x = TRAY_WIDTH - WALL_THICKNESS/2
# Distance between T-profiles = TRAY_WIDTH - WALL_THICKNESS = 117.5mm
# Frame T-slots should be at the same distance apart
FRAME_SCREW_HOLE = 4.5       # mm (for #8 wood screws)
FRAME_COUNTERSINK = 9.0      # mm (screw head recess)
FRAME_RAIL_WIDTH = 12.0      # mm (width of each side rail)
FRAME_RAIL_HEIGHT = 12.0     # mm (height/thickness of rails - increased for deeper T-slot)
# T-slot centered in rail, screws on cross beams
FRAME_BEAM_WIDTH = 12.0      # mm (width of cross beams)
FRAME_BEAM_HEIGHT = 4.0      # mm (height of cross beams - thinner than rails)
FRAME_SLOT_WIDTH = 5.0       # mm (comfortable fit for 4mm neck - 0.5mm clearance each side)
FRAME_CAVITY_WIDTH = 11.0    # mm (comfortable fit for 10mm head - 0.5mm clearance each side)
FRAME_CAVITY_HEIGHT = 4.0    # mm (comfortable fit for 3.5mm chamfered head - 0.5mm clearance)
FRAME_SLOT_HEIGHT = 2.5      # mm (comfortable fit for 2mm neck - 0.5mm clearance)
# Frame cavity is trapezoidal to match chamfered T-profile head
FRAME_STOP_THICKNESS = 2.5   # mm (wall at one end to stop tray)
FRAME_LENGTH = 180.0         # mm (length of frame, slightly shorter than tray)
# Frame width calculated so T-slots align with tray T-profiles
# T-slot distance = FRAME_WIDTH - FRAME_RAIL_WIDTH should equal T-profile distance
# T-profile distance = TRAY_WIDTH - WALL_THICKNESS
FRAME_WIDTH = TRAY_WIDTH - WALL_THICKNESS + FRAME_RAIL_WIDTH  # ~129.5mm

# End walls with cable slots
END_WALL_THICKNESS = 2.5     # mm
CABLE_SLOT_WIDTH = 25.0      # mm (width of cable slot)
CABLE_SLOT_HEIGHT = 20.0     # mm (height of slot, open at top)

# Cross beam positions along frame length (as ratio of frame length)
FRAME_BEAM_POSITIONS = [0.0, 0.5, 1.0]  # Front, middle, back

# ============================================
# Helper functions
# ============================================

def create_box(width, height, depth, x=0, y=0, z=0):
    """Create a box mesh at the specified position."""
    box = trimesh.creation.box(extents=[width, height, depth])
    box.apply_translation([x + width/2, y + height/2, z + depth/2])
    return box

def create_rounded_box(width, height, depth, radius, x=0, y=0, z=0, segments=8):
    """Create a box with rounded vertical edges."""
    # For simplicity, create a regular box (rounded corners add complexity)
    # Can enhance with cylinder corners later if needed
    return create_box(width, height, depth, x, y, z)

def create_cylinder(radius, height, x=0, y=0, z=0, segments=32):
    """Create a cylinder mesh at the specified position."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    cyl.apply_translation([x, y, z + height/2])
    return cyl

def create_cylinder_x(radius, length, x=0, y=0, z=0, segments=32):
    """Create a cylinder aligned along X axis."""
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=segments)
    # Rotate to align with X axis
    rotation = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    cyl.apply_transform(rotation)
    cyl.apply_translation([x + length/2, y, z])
    return cyl

def create_t_profile_upright(neck_width, neck_height, head_width, chamfer_height, head_flat, length, x=0, y=0, z=0):
    """
    Create an upright T-profile with chamfered head, pointing UP.
    Built from boxes with wedges subtracted for 45° chamfer.
    """
    parts = []

    # Neck - narrow vertical part
    neck = create_box(neck_width, length, neck_height,
                      x - neck_width/2, y, z)
    parts.append(neck)

    # Head block - full width, includes chamfer zone + flat top
    head_total_height = chamfer_height + head_flat
    head = create_box(head_width, length, head_total_height,
                      x - head_width/2, y, z + neck_height)
    parts.append(head)

    # Combine neck and head first
    result = parts[0]
    for part in parts[1:]:
        try:
            result = trimesh.boolean.union([result, part], engine='manifold')
        except:
            result = trimesh.util.concatenate([result, part])

    # Now subtract wedges to create 45° chamfer
    # Wedge on left side: triangle that removes material from left corner
    # Wedge on right side: triangle that removes material from right corner
    overhang = (head_width - neck_width) / 2  # How much head overhangs neck on each side

    # Create wedge using a rotated box (approximation) or prism
    # For 45° chamfer: overhang = chamfer_height
    # We'll create a triangular prism by subtracting

    # Left wedge - remove corner where head overhangs left of neck
    # This is a box that we position to cut the corner
    # Actually, let's use a proper triangular prism

    from shapely.geometry import Polygon as ShapelyPolygon

    # Left chamfer wedge (triangle in XZ, extruded along Y)
    left_wedge_points = [
        (x - head_width/2, z + neck_height),                    # bottom-left of head
        (x - neck_width/2, z + neck_height),                    # where neck meets head
        (x - neck_width/2, z + neck_height + chamfer_height),   # top of chamfer at neck edge
        (x - head_width/2, z + neck_height),                    # back to start
    ]
    # Simplify to triangle
    left_triangle = ShapelyPolygon([
        (-head_width/2, 0),           # outer bottom corner
        (-neck_width/2, 0),           # inner bottom (neck edge)
        (-neck_width/2, chamfer_height),  # inner top (neck edge + chamfer)
    ])
    left_wedge = trimesh.creation.extrude_polygon(left_triangle, height=length)
    # Rotate and position
    rotation = trimesh.transformations.rotation_matrix(-np.pi/2, [1, 0, 0])
    left_wedge.apply_transform(rotation)
    left_wedge.apply_translation([x, y, z + neck_height])

    # Right chamfer wedge (mirror of left)
    right_triangle = ShapelyPolygon([
        (head_width/2, 0),            # outer bottom corner
        (neck_width/2, 0),            # inner bottom (neck edge)
        (neck_width/2, chamfer_height),   # inner top (neck edge + chamfer)
    ])
    right_wedge = trimesh.creation.extrude_polygon(right_triangle, height=length)
    right_wedge.apply_transform(rotation)
    right_wedge.apply_translation([x, y, z + neck_height])

    # Subtract wedges to create chamfer
    try:
        result = trimesh.boolean.difference([result, left_wedge], engine='manifold')
        result = trimesh.boolean.difference([result, right_wedge], engine='manifold')
    except Exception as e:
        print(f"  Warning: Chamfer subtraction failed: {e}")

    return result

def create_t_slot_downward(slot_width, slot_height, cavity_width, cavity_height, chamfer_height, length, x=0, y=0, z=0):
    """
    Create a downward-opening T-slot for subtracting from frame rail underside.
    Built from simple boxes - slot + cavity.

    Opens at z, extends upward into the rail.
    """
    parts = []

    # Narrow slot at bottom (opening)
    slot = create_box(slot_width, length, slot_height + 1,  # +1 to cut through bottom
                      x - slot_width/2, y, z - 1)
    parts.append(slot)

    # Wide cavity above (captures T head)
    # Include chamfer zone in cavity for simplicity
    total_cavity = chamfer_height + cavity_height
    cavity = create_box(cavity_width, length, total_cavity,
                        x - cavity_width/2, y, z + slot_height)
    parts.append(cavity)

    # Combine slot and cavity
    try:
        result = trimesh.boolean.union(parts, engine='manifold')
    except:
        result = trimesh.util.concatenate(parts)

    return result

# ============================================
# Main generation functions
# ============================================

def generate_tray_shell():
    """Generate the tray body with end walls and cable slot notches."""

    outer_width = TRAY_WIDTH
    outer_length = TRAY_LENGTH
    outer_depth = TRAY_DEPTH + BOTTOM_THICKNESS

    inner_width = TRAY_WIDTH - 2 * WALL_THICKNESS
    inner_length = TRAY_LENGTH - 2 * END_WALL_THICKNESS  # Closed ends now
    inner_depth = TRAY_DEPTH + 1  # Open top

    print(f"=== Enclosed Cable Tray with End Walls ===")
    print(f"Outer: {outer_width}mm W x {outer_length}mm L x {outer_depth}mm D")
    print(f"End walls: {END_WALL_THICKNESS}mm thick")
    print(f"Cable slots: {CABLE_SLOT_WIDTH}mm x {CABLE_SLOT_HEIGHT}mm (open at top)")

    # Create outer shell (now includes end walls)
    outer = create_box(outer_width, outer_length, outer_depth, 0, 0, 0)

    # Create inner cavity (closed at ends)
    inner = create_box(
        inner_width,
        inner_length,
        inner_depth,
        WALL_THICKNESS,
        END_WALL_THICKNESS,  # Start after front end wall
        BOTTOM_THICKNESS
    )

    # Boolean difference to create enclosed trough
    print("Creating enclosed trough with end walls...")
    try:
        shell = trimesh.boolean.difference([outer, inner], engine='manifold')
    except Exception as e:
        print(f"Boolean failed: {e}")
        shell = outer

    # Create cable slot notches (open at top) on both ends
    slot_x = (TRAY_WIDTH - CABLE_SLOT_WIDTH) / 2  # Centered

    # Front slot (Y = 0)
    front_slot = create_box(
        CABLE_SLOT_WIDTH,
        END_WALL_THICKNESS + 2,
        CABLE_SLOT_HEIGHT + 1,  # Extends above top to create open notch
        slot_x,
        -1,
        outer_depth - CABLE_SLOT_HEIGHT
    )

    # Back slot (Y = TRAY_LENGTH - END_WALL_THICKNESS)
    back_slot = create_box(
        CABLE_SLOT_WIDTH,
        END_WALL_THICKNESS + 2,
        CABLE_SLOT_HEIGHT + 1,
        slot_x,
        TRAY_LENGTH - END_WALL_THICKNESS - 1,
        outer_depth - CABLE_SLOT_HEIGHT
    )

    # Subtract slots
    try:
        slots = trimesh.boolean.union([front_slot, back_slot], engine='manifold')
        shell = trimesh.boolean.difference([shell, slots], engine='manifold')
    except Exception as e:
        print(f"Slot subtraction failed: {e}")

    return shell

def generate_ribs():
    """Generate horizontal ribbed texture for exterior surfaces."""

    ribs = []
    outer_depth = TRAY_DEPTH + BOTTOM_THICKNESS  # No top wall now

    # Calculate number of ribs based on spacing
    num_ribs = int(outer_depth / RIB_SPACING)

    print(f"Generating {num_ribs} horizontal ribs (spacing: {RIB_SPACING}mm, depth: {RIB_DEPTH}mm)")

    for i in range(num_ribs):
        z_pos = i * RIB_SPACING + RIB_SPACING / 2

        if z_pos + RIB_WIDTH/2 > outer_depth:
            continue

        # Left side rib (on outer surface)
        left_rib = create_box(
            RIB_DEPTH,
            TRAY_LENGTH,
            RIB_WIDTH,
            -RIB_DEPTH,  # Protrude outward from left wall
            0,
            z_pos - RIB_WIDTH/2
        )
        ribs.append(left_rib)

        # Right side rib
        right_rib = create_box(
            RIB_DEPTH,
            TRAY_LENGTH,
            RIB_WIDTH,
            TRAY_WIDTH,  # Protrude outward from right wall
            0,
            z_pos - RIB_WIDTH/2
        )
        ribs.append(right_rib)

        # Bottom rib (only if above bottom thickness)
        if z_pos < BOTTOM_THICKNESS + RIB_WIDTH:
            bottom_rib = create_box(
                TRAY_WIDTH,
                TRAY_LENGTH,
                RIB_DEPTH,
                0,
                0,
                -RIB_DEPTH  # Protrude downward
            )
            ribs.append(bottom_rib)

    # Add ribs on bottom surface (running along length)
    num_bottom_ribs = int(TRAY_WIDTH / RIB_SPACING)
    for i in range(num_bottom_ribs):
        x_pos = i * RIB_SPACING + RIB_SPACING / 2

        if x_pos + RIB_WIDTH/2 > TRAY_WIDTH:
            continue

        bottom_rib = create_box(
            RIB_WIDTH,
            TRAY_LENGTH,
            RIB_DEPTH,
            x_pos - RIB_WIDTH/2,
            0,
            -RIB_DEPTH
        )
        ribs.append(bottom_rib)

    return ribs


def generate_tray_rails():
    """Generate full-length upright T-profiles on top of side walls."""

    rails = []
    rail_length = TRAY_LENGTH  # Full length of tray
    wall_top = TRAY_DEPTH + BOTTOM_THICKNESS  # Z position of wall top

    total_t_height = RAIL_NECK_HEIGHT + RAIL_CHAMFER_HEIGHT + RAIL_HEAD_FLAT

    print(f"Generating full-length upright T-rails:")
    print(f"  Neck: {RAIL_NECK_WIDTH}mm wide x {RAIL_NECK_HEIGHT}mm tall")
    print(f"  Head: {RAIL_HEAD_WIDTH}mm wide (with {RAIL_CHAMFER_HEIGHT}mm chamfer)")
    print(f"  Total height: {total_t_height}mm")
    print(f"  Wall thickness: {WALL_THICKNESS}mm (same as neck = one piece)")
    print(f"  Rail length: {rail_length}mm (full tray length)")

    # Left side rail - on top of left wall, centered on wall
    # Wall thickness = neck width, so they're naturally one piece
    left_x = WALL_THICKNESS / 2  # Center of left wall
    left_rail = create_t_profile_upright(
        neck_width=RAIL_NECK_WIDTH,
        neck_height=RAIL_NECK_HEIGHT,
        head_width=RAIL_HEAD_WIDTH,
        chamfer_height=RAIL_CHAMFER_HEIGHT,
        head_flat=RAIL_HEAD_FLAT,
        length=rail_length,
        x=left_x,
        y=0,
        z=wall_top  # Sits on top of wall
    )
    rails.append(left_rail)

    # Right side rail - on top of right wall, centered on wall
    right_x = TRAY_WIDTH - WALL_THICKNESS / 2  # Center of right wall
    right_rail = create_t_profile_upright(
        neck_width=RAIL_NECK_WIDTH,
        neck_height=RAIL_NECK_HEIGHT,
        head_width=RAIL_HEAD_WIDTH,
        chamfer_height=RAIL_CHAMFER_HEIGHT,
        head_flat=RAIL_HEAD_FLAT,
        length=rail_length,
        x=right_x,
        y=0,
        z=wall_top  # Sits on top of wall
    )
    rails.append(right_rail)

    return rails

def generate_rail_frame():
    """Generate single rail frame with T-slots on both sides (mounts to desk)."""

    parts = []

    # Inner width between the two rails (where tray fits)
    inner_width = FRAME_WIDTH - 2 * FRAME_RAIL_WIDTH

    print(f"=== Rail Frame ===")
    print(f"Frame: {FRAME_WIDTH}mm W x {FRAME_LENGTH}mm L")
    print(f"Rails: {FRAME_RAIL_WIDTH}mm wide, {FRAME_RAIL_HEIGHT}mm tall")
    print(f"T-slot: cavity {FRAME_CAVITY_WIDTH}mm, slot {FRAME_SLOT_WIDTH}mm")

    # Left rail (solid bar with T-slot on inner side)
    left_rail = create_box(
        FRAME_RAIL_WIDTH,
        FRAME_LENGTH,
        FRAME_RAIL_HEIGHT,
        0, 0, 0
    )
    parts.append(left_rail)

    # Right rail
    right_rail = create_box(
        FRAME_RAIL_WIDTH,
        FRAME_LENGTH,
        FRAME_RAIL_HEIGHT,
        FRAME_WIDTH - FRAME_RAIL_WIDTH, 0, 0
    )
    parts.append(right_rail)

    # Cross beams connecting the rails at the top
    beam_overlap = 5  # mm to extend into each rail
    beam_thickness = 3.0  # mm - thin but sturdy
    beam_z = FRAME_RAIL_HEIGHT - beam_thickness  # At top of rail

    for pos_ratio in FRAME_BEAM_POSITIONS:
        y_pos = pos_ratio * (FRAME_LENGTH - FRAME_BEAM_WIDTH)
        beam = create_box(
            inner_width + 2 * beam_overlap,  # Extends into both rails
            FRAME_BEAM_WIDTH,
            beam_thickness,
            FRAME_RAIL_WIDTH - beam_overlap,  # Start inside left rail
            y_pos,
            beam_z  # At top of rail
        )
        parts.append(beam)

    # Combine all frame parts
    print("Combining frame parts...")
    frame = parts[0]
    for part in parts[1:]:
        try:
            frame = trimesh.boolean.union([frame, part], engine='manifold')
        except:
            frame = trimesh.util.concatenate([frame, part])

    # Subtract downward-opening T-slots from both rails
    # T-slots are on the underside of the rails, opening DOWN
    # Tray's upright T-profiles slide into these from one end

    # T-slot dimensions (match tray T-profile with clearance)
    slot_width = RAIL_NECK_WIDTH + 1.0       # 5mm - slot width (4mm neck + clearance)
    slot_height = RAIL_NECK_HEIGHT + 0.5     # 2.5mm - slot depth
    cavity_width = RAIL_HEAD_WIDTH + 1.0     # 11mm - cavity width (10mm head + clearance)
    cavity_height = RAIL_HEAD_FLAT + 0.5     # 1mm - cavity above chamfer
    chamfer = RAIL_CHAMFER_HEIGHT + 0.5      # 3.5mm - chamfer height

    total_slot_depth = slot_height + chamfer + cavity_height  # Total depth into rail

    slot_length = FRAME_LENGTH - FRAME_STOP_THICKNESS + 1  # Leave stop wall at one end

    print(f"Creating downward-opening T-slots:")
    print(f"  Slot: {slot_width}mm wide x {slot_height}mm deep")
    print(f"  Cavity: {cavity_width}mm wide (with {chamfer}mm chamfer)")
    print(f"  Total depth: {total_slot_depth}mm")

    # T-slot centered in rail (screws are on cross beams now)
    # Left rail T-slot - centered, opening downward at Z=0
    left_x = FRAME_RAIL_WIDTH / 2  # Center of left rail
    left_t_slot = create_t_slot_downward(
        slot_width=slot_width,
        slot_height=slot_height,
        cavity_width=cavity_width,
        cavity_height=cavity_height,
        chamfer_height=chamfer,
        length=slot_length,
        x=left_x,
        y=FRAME_STOP_THICKNESS,
        z=-0.1  # Slight overlap to ensure clean cut at bottom
    )

    # Right rail T-slot - centered, opening downward at Z=0
    right_x = FRAME_WIDTH - FRAME_RAIL_WIDTH / 2  # Center of right rail
    right_t_slot = create_t_slot_downward(
        slot_width=slot_width,
        slot_height=slot_height,
        cavity_width=cavity_width,
        cavity_height=cavity_height,
        chamfer_height=chamfer,
        length=slot_length,
        x=right_x,
        y=FRAME_STOP_THICKNESS,
        z=-0.1
    )

    # Combine and subtract all slots
    try:
        all_slots = trimesh.boolean.union([left_t_slot, right_t_slot], engine='manifold')
        frame = trimesh.boolean.difference([frame, all_slots], engine='manifold')
    except Exception as e:
        print(f"  Warning: T-slot subtraction failed: {e}")

    # Add screw holes on the CROSS BEAMS (not rails, to avoid T-slot interference)
    # Cross beams are at Y positions defined by FRAME_BEAM_POSITIONS
    # Put TWO screw holes per beam (near each rail) = 6 total

    screw_inset = 8.0  # mm from rail edge to screw center
    hole_x_left = FRAME_RAIL_WIDTH + screw_inset  # Near left rail
    hole_x_right = FRAME_WIDTH - FRAME_RAIL_WIDTH - screw_inset  # Near right rail

    # Y positions match the cross beam positions
    hole_y_positions = [pos * (FRAME_LENGTH - FRAME_BEAM_WIDTH) + FRAME_BEAM_WIDTH/2
                        for pos in FRAME_BEAM_POSITIONS]

    # Subtract screw holes (2 per beam = 6 total)
    for y_pos in hole_y_positions:
        for x_pos in [hole_x_left, hole_x_right]:
            shaft = create_cylinder(
                FRAME_SCREW_HOLE / 2,
                FRAME_RAIL_HEIGHT + 2,
                x_pos, y_pos, -1
            )
            countersink = create_cylinder(
                FRAME_COUNTERSINK / 2,
                4.0,  # 4mm deep countersink
                x_pos, y_pos, -0.1
            )
            try:
                hole = trimesh.boolean.union([shaft, countersink], engine='manifold')
                frame = trimesh.boolean.difference([frame, hole], engine='manifold')
            except:
                pass

    return frame

def generate_cable_tray():
    """Generate the cable tray with T-profiles that slide into the rail frame."""

    print("\n=== Generating Cable Tray ===\n")

    # Generate main shell (with end walls and cable slots)
    shell = generate_tray_shell()

    # Ribs removed to reduce filament usage
    # ribs = generate_ribs()

    # Generate T-profiles on sides (slide into rail frame)
    rails = generate_tray_rails()

    # Combine all solid parts
    print("\nCombining all parts...")
    all_parts = [shell] + rails  # No ribs

    result = all_parts[0]
    for i, part in enumerate(all_parts[1:], 1):
        try:
            result = trimesh.boolean.union([result, part], engine='manifold')
        except Exception as e:
            print(f"Warning: Union {i} failed, using concatenate")
            result = trimesh.util.concatenate([result, part])

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

    # Generate the tray
    tray = generate_cable_tray()

    # Get bounds for info
    bounds = tray.bounds
    size = bounds[1] - bounds[0]
    print(f"\nTray dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export tray STL
    tray_path = os.path.join(script_dir, "cable_tray.stl")
    tray.export(tray_path)
    print(f"Tray STL exported to: {tray_path}")

    # Generate rail frame
    print("\n")
    frame = generate_rail_frame()

    bounds = frame.bounds
    size = bounds[1] - bounds[0]
    print(f"Frame dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export frame STL
    frame_path = os.path.join(script_dir, "rail_frame.stl")
    frame.export(frame_path)
    print(f"Frame STL exported to: {frame_path}")

    print("\n" + "="*50)
    print("ASSEMBLY INSTRUCTIONS:")
    print("="*50)
    print("1. Print 1x cable_tray.stl")
    print("2. Print 1x rail_frame.stl")
    print("3. Screw the rail frame to desk underside (6 screws)")
    print("4. Slide tray into frame from the open end")
    print("5. Tray stops at the frame's stop walls")
    print("="*50)

if __name__ == "__main__":
    main()
