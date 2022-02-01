import webbrowser
import bpy

class FSBLinkToTwitterOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.link_to_twitter"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox"

    def execute(self, context):
        webbrowser.open("https://twitter.com/funisaki")
        return{'FINISHED'}
class FSBLinkToDiscordOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.link_to_discord"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox"

    def execute(self, context):
        webbrowser.open("https://discord.gg/yJzvyt6qpz")
        return{'FINISHED'}
class FSBLinkToWebOperator(bpy.types.Operator):
    bl_idname = "funi_shader_box.link_to_web"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox"

    def execute(self, context):
        webbrowser.open("https://tools.funisaki.com/shaderbox")
        return{'FINISHED'}