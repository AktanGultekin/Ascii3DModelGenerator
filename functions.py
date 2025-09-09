import math
import numpy as np


ASCII_CHARS = "@%#*+=-:. "

def rotation_matrix(rx, ry, rz):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rz @ Ry @ Rx

def mesh_to_shaded_points(m, light_dir=np.array([1,1,1])):
    """Calculate from mesh organized by vertices and parts """
    light_dir = light_dir / np.linalg.norm(light_dir)
    verts = m.vectors.reshape(-1, 3)
    norms = np.repeat(m.normals, 3, axis=0)  # her vertex için normal
    brightness = np.dot(norms, light_dir)
    brightness = np.clip(brightness, 0, 1)
    return verts, brightness

def project_points(points, width, height, scale=1.0, rx=0, ry=0, rz=0):
    """Rotate, scale, center ve XY projectıon"""
    R = rotation_matrix(rx, ry, rz)
    pts = (R @ points.T).T * scale
    center = pts.mean(axis=0)
    pts -= center
    xs, ys, zs = pts[:,0], pts[:,1], pts[:,2]

    span = max(np.ptp(xs), np.ptp(ys), 1e-6)
    xs_norm = (xs / span) * (width/2 * 0.9) + width/2
    ys_norm = (ys / span) * (height/2 * 0.9) + height/2
    return np.vstack([xs_norm, ys_norm, zs]).T

def points_to_ascii_shaded(points_proj, brightness, cols=120, rows=60, chars=ASCII_CHARS):
    grid_bright = np.full((rows, cols), np.nan)
    xs, ys = points_proj[:,0], points_proj[:,1]

    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()
    ix = np.clip(((xs - xmin) / (xmax - xmin) * (cols-1)).astype(int), 0, cols-1)
    iy = np.clip(((ys - ymin) / (ymax - ymin) * (rows-1)).astype(int), 0, rows-1)

    for xg, yg, b in zip(ix, iy, brightness):
        prev = grid_bright[yg, xg]
        if np.isnan(prev) or b > prev:   # daha parlak olanı al
            grid_bright[yg, xg] = b

    out_lines = []
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            if np.isnan(grid_bright[r, c]):
                line_chars.append(" ")
            else:
                idx = int(grid_bright[r, c] * (len(chars)-1))
                line_chars.append(chars[idx])
        out_lines.append("".join(line_chars))
    return "\n".join(out_lines)