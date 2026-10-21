"""Native FreeCAD headless job; no GUI imports, output paths supplied by the adapter."""
import json
import os
from pathlib import Path
import runpy
import sys


def main():
    # Debian's compiled FreeCAD module needs the distribution Python (3.11).
    sys.path.insert(0, '/usr/lib/freecad-python3/lib')
    sys.path.insert(0, '/usr/lib/freecad/lib')
    import FreeCAD as App
    import Part
    action, source, target = sys.argv[1:]
    target = Path(target)
    if action == 'version':
        print('.'.join(App.Version()[:3])); return
    if action == 'execute':
        os.environ['ARTCRAFT_JOB_OUTPUT'] = str(target)
        runpy.run_path(source, run_name='__main__')
        return
    document = App.openDocument(source)
    try:
        document.recompute()
        shapes = [obj for obj in document.Objects if hasattr(obj, 'Shape') and not obj.Shape.isNull()]
        if action == 'export_step':
            if not shapes:
                raise ValueError('No native shapes to export')
            Part.export(shapes, str(target)); return
        objects = []
        dependencies = []
        for obj in document.Objects:
            row = {'name': obj.Name, 'label': obj.Label, 'type': obj.TypeId}
            row['invalid'] = 'Invalid' in obj.State
            if obj in shapes:
                row.update(volume=obj.Shape.Volume, valid=obj.Shape.isValid(), solids=len(obj.Shape.Solids))
            row['dimensions_mm'] = {key: float(getattr(obj, key).Value) for key in ('Length', 'Width', 'Height', 'Radius') if key in obj.PropertiesList}
            objects.append(row)
            for key in obj.PropertiesList:
                kind = obj.getTypeIdOfProperty(key)
                if kind in ('App::PropertyFile', 'App::PropertyFileIncluded'):
                    value = str(getattr(obj, key))
                    if value: dependencies.append(value)
            if hasattr(obj, 'LinkedObject') and obj.LinkedObject and obj.LinkedObject.Document != document:
                dependencies.append(obj.LinkedObject.Document.FileName)
        target.write_text(json.dumps({'document': document.Name, 'objects': objects,
                                     'dependencies': sorted(set(dependencies))}, indent=2))
    finally:
        App.closeDocument(document.Name)


if __name__ == '__main__':
    main()
