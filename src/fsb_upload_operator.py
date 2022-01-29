import bpy
import webbrowser
import requests
import base64
import os
from . import rna_xml_alt

PREVIEW_SCENE_PATH = os.path.join(os.path.dirname(__file__), "preview.blend","Scene")
UPLOAD_URL = 'https://tools.funisaki.com/api/shaderbox/upload'

class FSBUploadOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.upload"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox"

    def execute(self, context):
        temp_path = bpy.app.tempdir
        preview_file_path = temp_path + "funishaderboxpreviewresult.png"
        nodetree_file_path = temp_path + "node_tree.xml"
        material = bpy.context.active_object.active_material
        bpy.ops.wm.append(filepath=PREVIEW_SCENE_PATH + "ShaderBoxPreviewScene", directory=PREVIEW_SCENE_PATH, filename="ShaderBoxPreviewScene")
        bpy.data.scenes["ShaderBoxPreviewScene"].render.filepath = preview_file_path
        bpy.data.scenes["ShaderBoxPreviewScene"].objects[2].data.materials[0] = material
        f = open(nodetree_file_path,"w+")
        rna_xml_alt.rna2xml(fw=f.write, root_node="Root", root_rna=material.node_tree, method='ATTR')
        f.close()
        
        bpy.ops.render.render(animation=False, write_still=True, use_viewport=False, layer='', scene="ShaderBoxPreviewScene")
        bpy.ops.scene.delete({"scene": bpy.data.scenes["ShaderBoxPreviewScene"]})
        with open(nodetree_file_path, "rb") as xml_file:
            xml_base64 = base64.b64encode(xml_file.read())
        with open(preview_file_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read())
        myobj = {"xml": xml_base64,"image": image_base64}
        with requests.post(UPLOAD_URL, data = myobj) as resp:
            res = resp
        data = res.json()
        webbrowser.open(data["url"])

        return{'FINISHED'}
