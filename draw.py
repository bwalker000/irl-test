import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_diamond(x, y, diam):
    """
    Draw a diamond.

    Parameters:
    - x = x center
    - y = y center
    - diam = diameter of the diamond
    """

    diamond_half = diam/2 * 1.2  # Same size as in matrix
    diamond = patches.Polygon([
        (x, y + diamond_half),          # top
        (x + diamond_half, y),          # right
        (x, y - diamond_half),          # bottom
        (x - diamond_half, y),          # left
    ], closed=True, facecolor='black', edgecolor='black', lw=1)
    
    return diamond
