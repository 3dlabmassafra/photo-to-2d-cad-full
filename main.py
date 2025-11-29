from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from .process import image_to_contours_bytes, contours_to_svg, contours_to_dxf
from .feature_script import generate_featurescript_from_polygons

app = FastAPI()
app.add_middleware(CORSORMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.post('/api/upload')
async def upload_image(file: UploadFile = File(...), threshold: int = Form(128)):
    data = await file.read()
    polygons = image_to_contours_bytes(data, threshold=threshold)
    svg = contours_to_svg(polygons)
    return JSONResponse({'polygons': polygons, 'svg': svg})

@app.post('/api/export/dxf')
async def export_dxf(file: UploadFile = File(...), threshold: int = Form(128)):
    data = await file.read()
    polygons = image_to_contours_bytes(data, threshold=threshold)
    return Response(content=contours_to_dxf(polygons), media_type='application/dxf')

@app.post('/api/export/featurescript')
async def export_fs(file: UploadFile = File(...), threshold: int = Form(128)):
    data = await file.read()
    polygons = image_to_contours_bytes(data, threshold=threshold)
    fs = generate_featurescript_from_polygons(polygons)
    return Response(content=fs, media_type='text/plain')
