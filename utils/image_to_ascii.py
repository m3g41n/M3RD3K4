"""Image loading and the numeric helpers used to turn pixels into ASCII cells."""
from collections import deque

import numpy as np


def load_gray(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64) / 255.0


def fit_cells(px_w, px_h, max_cols, max_rows, cell_aspect=2.0):
    """Largest (cols, rows) that fits, keeping the image proportions.
    A terminal cell is ~2x taller than wide, hence `cell_aspect`."""
    s = min(max_cols / px_w, max_rows * cell_aspect / px_h)
    return max(1, int(px_w * s)), max(1, int(px_h * s / cell_aspect))


def dilate(m, n=1):
    out = m.copy()
    for _ in range(n):
        p = out.copy()
        p[1:] |= out[:-1]
        p[:-1] |= out[1:]
        p[:, 1:] |= out[:, :-1]
        p[:, :-1] |= out[:, 1:]
        out = p
    return out


def flood_from_border(free):
    """Cells of `free` that are 4-connected to the image border."""
    h, w = free.shape
    seen = np.zeros_like(free, dtype=bool)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if free[y, x] and not seen[y, x]:
                seen[y, x] = True
                stack.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if free[y, x] and not seen[y, x]:
                seen[y, x] = True
                stack.append((y, x))
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and free[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return seen


def label_components(mask):
    """4-connected component labelling; returns (labels, count). 0 = background."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if labels[y0, x0]:
            continue
        n += 1
        labels[y0, x0] = n
        dq = deque([(y0, x0)])
        while dq:
            y, x = dq.popleft()
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not labels[ny, nx]:
                    labels[ny, nx] = n
                    dq.append((ny, nx))
    return labels, n


def sample_bilinear(arr, U, V):
    """Sample `arr` at normalised coords (U right, V down), 0 outside the image."""
    H, W = arr.shape
    x = U * W - 0.5
    y = V * H - 0.5
    x0 = np.floor(x).astype(np.intp)
    y0 = np.floor(y).astype(np.intp)
    fx = x - x0
    fy = y - y0

    def g(yy, xx):
        inside = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
        return np.where(inside, arr[np.clip(yy, 0, H - 1), np.clip(xx, 0, W - 1)], 0.0)

    return (g(y0, x0) * (1 - fx) * (1 - fy) + g(y0, x0 + 1) * fx * (1 - fy)
            + g(y0 + 1, x0) * (1 - fx) * fy + g(y0 + 1, x0 + 1) * fx * fy)


def block_mean(a, by, bx):
    h, w = a.shape
    return a.reshape(h // by, by, w // bx, bx).mean(axis=(1, 3))


def sample_grid(rows, cols, sy, sx):
    """Normalised coordinate grids for a (rows*sy) x (cols*sx) supersampled cell grid."""
    ys = (np.arange(rows * sy) + 0.5) / (rows * sy)
    xs = (np.arange(cols * sx) + 0.5) / (cols * sx)
    return np.meshgrid(xs, ys)
