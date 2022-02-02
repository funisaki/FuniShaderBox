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

    def delete_preview_scene(self, scene):
        collection = bpy.data.collections[-1]
        all_objects = collection.all_objects
        for obj in all_objects:
            if(obj.type == "LIGHT"):
                bpy.data.objects.remove(obj)
                bpy.data.lights.remove(bpy.data.lights[-1])
                break
        for obj in all_objects:
            if(obj.type == "CAMERA"):
                bpy.data.objects.remove(obj)
                bpy.data.cameras.remove(bpy.data.cameras[-1])
                break
        for obj in range(len(all_objects)):
            bpy.data.objects.remove(all_objects[-1])
        bpy.data.collections.remove(bpy.data.collections[-1])
        bpy.data.worlds.remove(bpy.data.worlds[-1])
        for mesh in bpy.data.meshes:
            if(mesh.name.split('.')[0] == "__FSBFloor__" or mesh.name.split('.')[0] == "__FSBSample__"):
                bpy.data.meshes.remove(mesh)
        for mats in bpy.data.materials:
            if(mats.name.split('.')[0] == "__FSBFloor1__" or mats.name.split('.')[0] == "__FSBFloor2__"):
                bpy.data.materials.remove(mats)
        bpy.ops.scene.delete({"scene": scene})
    
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

    IGNORE_LIST=["GROUP", "TEX_IMAGE"]
    def check_nodes(self,nodes):
        msgs = {"GROUP": "グループノード","TEX_IMAGE": "画像テクスチャノード"}
        for node in nodes:
            if(node.type in self.IGNORE_LIST):
                self.report({'ERROR'},msgs[node.type]+"が含まれているためアップロード出来ません.")
                return False

        return True
        
    def execute(self, context):
        temp_path = bpy.app.tempdir
        preview_file_path = temp_path + "funishaderboxpreviewresult.png"
        material = bpy.context.active_object.active_material
        if(material == None):
            self.report({'ERROR'},"マテリアルが選択されていません。")
            return {'FINISHED'}
        valid = self.check_nodes(material.node_tree.nodes)
        if(not valid):
            return{'FINISHED'} 

        bpy.ops.wm.append(filepath=PREVIEW_SCENE_PATH + "ShaderBoxPreviewScene", directory=PREVIEW_SCENE_PATH, filename="ShaderBoxPreviewScene")
        preview_scene = bpy.data.scenes[-1]
        preview_scene.render.filepath = preview_file_path
        preview_scene.objects[2].data.materials[0] = material
        node_group_list = list()
        self.read_node_tree(temp_path, material.node_tree, node_group_list)
        bpy.ops.render.render(animation=False, write_still=True, use_viewport=False, layer='', scene=preview_scene.name)
        self.delete_preview_scene(preview_scene)
        with open(preview_file_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read())
        url = 'https://tools.funisaki.com/api/shaderbox/upload'
        myobj = {"shader_def": json.dumps({"node_group_list": node_group_list}, separators=(',', ':')) ,"image": image_base64}
        with requests.post(url, data = myobj) as resp:
            res = resp
        data = res.json()
        webbrowser.open(data["url"])

        return{'FINISHED'}
