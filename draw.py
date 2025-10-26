import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_diamond(cx, cy, size, filled=True, linewidth=1):
    """
    Draw a diamond (rotated square) centered at (cx, cy) with given size.
    
    Args:
        cx: x-coordinate of center
        cy: y-coordinate of center
        size: size (width/height) of the diamond
        filled: whether to fill the diamond (default True)
        linewidth: thickness of the diamond border (default 1)
    
    Returns:
        matplotlib Polygon patch
    """
    half = size / 2
    vertices = [
        (cx, cy + half),      # top
        (cx + half, cy),      # right
        (cx, cy - half),      # bottom
        (cx - half, cy),      # left
    ]
    
    if filled:
        return patches.Polygon(vertices, closed=True, facecolor='black', edgecolor='black', lw=linewidth)
    else:
        return patches.Polygon(vertices, closed=True, facecolor='white', edgecolor='black', lw=linewidth)
