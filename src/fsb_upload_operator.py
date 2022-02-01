import bpy
import webbrowser
import requests
import base64
import os
from . import rna_xml_alt
import json

PREVIEW_SCENE_PATH = os.path.join(os.path.dirname(__file__), "preview.blend","Scene")
UPLOAD_URL = 'https://tools.funisaki.com/api/shaderbox/upload'

class FSBUploadOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.upload"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox"

    def read_node_tree(self, temp_path, node_tree, tree_list):
        node_tree_dups = 0
        for t in tree_list:
            if(t["name"] == node_tree.name):
                node_tree_dups = 1
                break
        if(node_tree_dups == 1):
            return

        nodetree_file_path = temp_path + str(len(tree_list)) + "node_tree.xml"
        
        f = open(nodetree_file_path,"w+")
        rna_xml_alt.rna2xml(fw=f.write, root_node="Root", root_rna=node_tree, method='ATTR')
        f.close()
        with open(nodetree_file_path, "rb") as xml_file:
            xml = xml_file.read().decode('utf-8')
        tree_list.append({'name': node_tree.name, 'xml': xml})
        for n in node_tree.nodes:
            if(n.type == "GROUP"):
                self.read_node_tree(temp_path, n.node_tree, tree_list)

    def execute(self, context):
        temp_path = bpy.app.tempdir
        preview_file_path = temp_path + "funishaderboxpreviewresult.png"
        material = bpy.context.active_object.active_material
        bpy.ops.wm.append(filepath=PREVIEW_SCENE_PATH + "ShaderBoxPreviewScene", directory=PREVIEW_SCENE_PATH, filename="ShaderBoxPreviewScene")
        bpy.data.scenes["ShaderBoxPreviewScene"].render.filepath = preview_file_path
        bpy.data.scenes["ShaderBoxPreviewScene"].objects[2].data.materials[0] = material
        node_group_list = list()
        self.read_node_tree(temp_path, material.node_tree, node_group_list)

        bpy.ops.render.render(animation=False, write_still=True, use_viewport=False, layer='', scene="ShaderBoxPreviewScene")
        bpy.ops.scene.delete({"scene": bpy.data.scenes["ShaderBoxPreviewScene"]})
        
        with open(preview_file_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read())
        url = 'https://tools.funisaki.com/api/shaderbox/upload'
        myobj = {"shader_def": json.dumps({"node_group_list": node_group_list}, separators=(',', ':')) ,"image": image_base64}
        with requests.post(url, data = myobj) as resp:
            res = resp
        data = res.json()
        webbrowser.open(data["url"])

        return{'FINISHED'}
