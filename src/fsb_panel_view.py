import bpy

class FSBPanelView(bpy.types.Panel):
    bl_idname = "NODE_PT_funi_shader_box_view"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "ShaderBox"
    bl_region_type = "UI"
    bl_category = "ShaderBox"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("funi_shader_box.upload", text="アップロード", icon="OUTLINER_COLLECTION")
        layout.separator()
        layout.label(text="シェーダーID")
        layout.prop(scene, "funiShadeBoxItemId", text="")
        layout.operator("funi_shader_box.import", text="インポート", icon="OUTLINER_COLLECTION")
        layout.separator()

        row = layout.row()
        box = row.box()
        box_row = box.row()
        box_column = box_row.column()
        box_column.operator("funi_shader_box.link_to_web", text="ShaderBoxのサイトへ")
        box_column.label(text="お問い合わせ")
        box_column.operator("funi_shader_box.link_to_twitter", text="Twitter")
        box_column.operator("funi_shader_box.link_to_discord", text="Discord")
