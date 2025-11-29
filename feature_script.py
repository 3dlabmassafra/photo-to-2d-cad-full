TEMPLATE = '''// FeatureScript generato automaticamente (unità: mm)
annotation {"Name":"generated_profile"}
export const generated_profile = defineFeature(function(context is Context, id is Id, definition is map)
{
    var sketch = newSketchOnPlane(context, id + "sketch", {"plane": qSketchPlaneDefault});
{adds}
    skSolve(sketch);
});
'''

def generate_featurescript_from_polygons(polygons):
    adds = []
    for i, poly in enumerate(polygons):
        pts = ', '.join([f'vector({x} mm, {y} mm)' for x, y in poly])
        adds.append(f'    skPolyline(sketch, "poly{i}", [{pts}]);')
    return TEMPLATE.format(adds="\n".join(adds))
