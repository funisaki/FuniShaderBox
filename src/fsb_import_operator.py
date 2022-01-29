import bpy
import requests
import xml.dom.minidom
from . import rna_xml_alt

class FSBImportOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.import"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox" 
    
    def createNodesAndLinks(self,node_tree,root_xml):
        nodes_xml = root_xml.getElementsByTagName("nodes")[0]
        links_xml = root_xml.getElementsByTagName("links")[0]
        def create(xml, type="NODE"):
            if xml.nodeType != xml.ELEMENT_NODE:
                return
            if(type== "NODE"):
                bpy.ops.node.add_node(type= xml.nodeName, use_transform=True)
                node_tree.nodes[-1].name = xml.attributes["name"].value
            elif(type=="LINK"):
                fromNodeId = xml.attributes["from_node"].value.split("::")[1]
                fromSocketId = xml.getElementsByTagName("from_socket")[0].childNodes[1].attributes["identifier"].value
                toNodeId = xml.attributes["to_node"].value.split("::")[1]
                toSocketId = xml.getElementsByTagName("to_socket")[0].childNodes[1].attributes["identifier"].value
                for inp in node_tree.nodes.get(fromNodeId).outputs:
                    if(fromSocketId == inp.identifier):
                        fromSocket = inp
                for inp in node_tree.nodes.get(toNodeId).inputs:
                    if(toSocketId == inp.identifier):
                        toSocket = inp
                node_tree.links.new(fromSocket,toSocket)
        for xml in nodes_xml.childNodes:
            create(xml, type="NODE")
        for xml in links_xml.childNodes:
            create(xml, type="LINK")
        
    def execute(self, context):
        scene = context.scene 
        url = 'https://l.funisaki.com/shaderbox/%s/nodetree.xml' % scene.funiShadeBoxItemId
        x = requests.get(url)
        xml_nodes = xml.dom.minidom.parseString(x.content)
        root_xml = xml_nodes.getElementsByTagName("ShaderNodeTree")[0]
        material = bpy.context.active_object.active_material
        for n in material.node_tree.nodes:
            material.node_tree.nodes.remove(n)
        self.createNodesAndLinks(material.node_tree, root_xml)
        rna_xml_alt.xml2rna(root_xml, root_rna=material.node_tree)
        return{'FINISHED'}