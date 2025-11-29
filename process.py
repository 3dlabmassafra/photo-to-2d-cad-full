PX_TO_MM = 1.0  # 1 px = 1 mm

import io
import numpy as np
import cv2
from PIL import Image

def image_to_contours_bytes(image_bytes: bytes, threshold: int = 128, approx_eps: float = 2.0):
    img = Image.open(io.BytesIO(image_bytes)).convert('L')
    arr = np.array(img)

    max_dim = 1600
    h, w = arr.shape
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        arr = cv2.resize(arr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)

    arr = cv2.GaussianBlur(arr, (3,3), 0)
    _, th = cv2.threshold(arr, threshold, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    polys = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, approx_eps, True)
        poly = [
            (
                float(p[0][0] / scale) * PX_TO_MM,
                float(p[0][1] / scale) * PX_TO_MM
            )
            for p in approx
        ]
        if len(poly) >= 3:
            polys.append(poly)
    return polys

def contours_to_svg(polygons, width=None, height=None):
    xs = [x for poly in polygons for (x,y) in poly] or [0,100]
    ys = [y for poly in polygons for (x,y) in poly] or [0,100]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    width = maxx - minx or 100
    height = maxy - miny or 100

    paths = []
    for poly in polygons:
        d = 'M ' + ' L '.join(f'{x} {y}' for x,y in poly) + ' Z'
        paths.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="1"/>')

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">\n' + "\n".join(paths) + "\n</svg>"
    return svg

def contours_to_dxf(polygons):
    import ezdxf, io
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    for poly in polygons:
        msp.add_lwpolyline([(float(x), float(y)) for (x, y) in poly], close=True)
    f = io.BytesIO()
    doc.write(f)
    f.seek(0)
    return f.read()
