#!/usr/bin/env python3
"""
Simple Z-Bracket - T-head overhang rests on the bottom lip
"""

import trimesh
import numpy as np

# Bracket dimensions
THICKNESS = 3.0      # mm - material thickness
LENGTH = 40.0        # mm - bracket length (along tray)

# Top plate (screws to desk)
TOP_WIDTH = 15.0     # mm

# Vertical drop (matches T-head thickness: 0.5mm flat + 3mm chamfer)
DROP = 3.5           # mm

# Bottom lip (T-head rests on this)
LIP_WIDTH = 8.0      # mm

# Screw holes
SCREW_DIA = 4.5      # mm

def create_box(w, l, h, x=0, y=0, z=0):
    box = trimesh.creation.box(extents=[w, l, h])
    box.apply_translation([x + w/2, y + l/2, z + h/2])
    return box

def create_cylinder(r, h, x=0, y=0, z=0):
    cyl = trimesh.creation.cylinder(radius=r, height=h, sections=32)
    cyl.apply_translation([x, y, z + h/2])
    return cyl

def generate_bracket():
    """
    Side view (X-Z plane, looking along Y):

              _____    Z=0 (desk surface)
             |     |   <- Top plate (screws to desk)
             |_____|
             |
             |         <- Vertical (DROP = T-head thickness)
        _____|
       |     |         <- Lip (T-head rests on top)
       |_____|

       X ->
    """

    parts = []

    # Top plate: sits at Z = -THICKNESS to Z = 0
    # Extends from X = 0 to X = TOP_WIDTH
    top = create_box(TOP_WIDTH, LENGTH, THICKNESS, 0, 0, -THICKNESS)
    parts.append(top)

    # Vertical: at LEFT edge of top plate
    # From Z = -THICKNESS down to Z = -THICKNESS - DROP
    vert = create_box(THICKNESS, LENGTH, DROP, 0, 0, -THICKNESS - DROP)
    parts.append(vert)

    # Lip: at bottom of vertical, extends LEFT (outward, to catch T-head)
    # At Z = -THICKNESS - DROP - THICKNESS
    lip = create_box(LIP_WIDTH, LENGTH, THICKNESS, -LIP_WIDTH + THICKNESS, 0, -THICKNESS - DROP - THICKNESS)
    parts.append(lip)

    # Combine
    result = parts[0]
    for p in parts[1:]:
        result = trimesh.boolean.union([result, p], engine='manifold')

    # Screw holes in top plate
    for y in [LENGTH * 0.25, LENGTH * 0.75]:
        hole = create_cylinder(SCREW_DIA / 2, THICKNESS + 2, TOP_WIDTH / 2, y, -THICKNESS - 1)
        result = trimesh.boolean.difference([result, hole], engine='manifold')

    return result

if __name__ == "__main__":
    import os

    print(f"Z-Bracket: {TOP_WIDTH}mm top, {DROP}mm drop, {LIP_WIDTH}mm lip")
    print(f"Thickness: {THICKNESS}mm, Length: {LENGTH}mm")

    bracket = generate_bracket()

    bounds = bracket.bounds
    size = bounds[1] - bounds[0]
    print(f"Size: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")

    path = os.path.join(os.path.dirname(__file__), "z_bracket.stl")
    bracket.export(path)
    print(f"Saved: {path}")
    print("\nPrint 2-4 brackets. Screw to desk, slide tray so T-heads rest on lips.")
