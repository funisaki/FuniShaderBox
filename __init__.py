import os
import bpy
from .src import (fsb_panel_view, fsb_import_operator, fsb_upload_operator)

bl_info = {
    "name": "ShaderBox",
    "author": "Funisaki",
    "version": (0, 1),
    "blender": (3,0, 0),
    "location": "File > Import-Export",
    "description": "",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "https://github.com/funisaki/FuniShaderBox/issues",
    "category": "Import-Export",
}

classes = [
    fsb_upload_operator.FSBUploadOperator,
    fsb_import_operator.FSBImportOperator,
    fsb_panel_view.FSBPanelView
]

def init_props():
    scene = bpy.types.Scene
    scene.funiShadeBoxItemId = bpy.props.StringProperty(
        name="funiShadeBoxItemId",
        description="FuniShadeBoxItemId",
        default="",
        maxlen=1024,
        )
        
def clear_props():
    scene = bpy.types.Scene
    del scene.funiShadeBoxItemId

def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()

def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()