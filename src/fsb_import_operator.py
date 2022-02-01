import bpy
import requests
import xml.dom.minidom
from . import rna_xml_alt
import json

class FSBImportOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.import"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox" 
    def createShaderNodeGroup(self,name, xml_string):
        with xml.dom.minidom.parseString(xml_string) as node_group_xml:
            new_group = bpy.data.node_groups.new(name, "ShaderNodeTree")
            self.node_group_map[name] = new_group.name
            root_xml = node_group_xml.getElementsByTagName("ShaderNodeTree")[0]
            self.createNodesAndLinks(new_group, root_xml,type="NODE")
            self.createNodesAndLinks(new_group, root_xml,type="LINK")
            rna_xml_alt.xml2rna(root_xml, root_rna=new_group, node_group_map=self.node_group_map)
            self.createNodesAndLinks(new_group, root_xml,type="LINK")

    def createNodesAndLinks(self,node_tree,root_xml, type="NODE"):
        nodes_xml = root_xml.getElementsByTagName("nodes")[0]
        links_xml = root_xml.getElementsByTagName("links")[0]
        def create(node_xml, type="NODE"):
            if node_xml.nodeType != node_xml.ELEMENT_NODE:
                return
            if(type== "NODE"):
                new_node = node_tree.nodes.new(node_xml.nodeName)
                new_node.name = node_xml.attributes["name"].value
            elif(type=="LINK"):
                fromNodeId = node_xml.attributes["from_node"].value.split("::")[1]
                fromSocketId = node_xml.getElementsByTagName("from_socket")[0].childNodes[1].attributes["identifier"].value
                toNodeId = node_xml.attributes["to_node"].value.split("::")[1]
                toSocketId = node_xml.getElementsByTagName("to_socket")[0].childNodes[1].attributes["identifier"].value
                
                if(len(node_tree.nodes.get(fromNodeId).outputs) == 0):
                    return
                fromSocket = node_tree.nodes.get(fromNodeId).outputs[0]
                for inp in node_tree.nodes.get(fromNodeId).outputs:
                    if(fromSocketId == inp.identifier):
                        fromSocket = inp
                if(len(node_tree.nodes.get(toNodeId).inputs) == 0):
                    return
                toSocket = node_tree.nodes.get(toNodeId).inputs[0]
                for inp in node_tree.nodes.get(toNodeId).inputs:
                    if(toSocketId == inp.identifier):
                        toSocket = inp
                node_tree.links.new(fromSocket,toSocket)
        if(type == "NODE"):
            for node_xml in nodes_xml.childNodes:
                create(node_xml, type="NODE")
        if(type == "LINK"):
            for node_xml in links_xml.childNodes:
                create(node_xml, type="LINK")
        
        
    def execute(self, context):
        self.node_group_map = {}
        scene = context.scene 
        url = 'https://l.funisaki.com/shaderbox/%s/shaderdef.json' % scene.funiShadeBoxItemId
        x = requests.get(url)
        shader_def = json.loads(x.content)
        node_group_list = shader_def["node_group_list"]
        node_group_list.reverse()
        root_node_tree_pack = node_group_list.pop()
        for node_tree_pack in node_group_list:
            xml_string = node_tree_pack["xml"]
            self.createShaderNodeGroup(node_tree_pack["name"],xml_string)
        with xml.dom.minidom.parseString(root_node_tree_pack["xml"]) as xml_nodes:
            root_xml = xml_nodes.getElementsByTagName("ShaderNodeTree")[0]
            material = bpy.context.active_object.active_material
            for n in material.node_tree.nodes:
                material.node_tree.nodes.remove(n)
            self.createNodesAndLinks(material.node_tree, root_xml, type="NODE")
            self.createNodesAndLinks(material.node_tree, root_xml, type="LINK")
            rna_xml_alt.xml2rna(root_xml, root_rna=material.node_tree, node_group_map=self.node_group_map)
            self.createNodesAndLinks(material.node_tree, root_xml, type="LINK")
        
        return{'FINISHED'}