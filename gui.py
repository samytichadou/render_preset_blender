import bpy


class RNDRP_UL_available_presets(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "name", text="", emboss=False)


# main panel
class RNDRP_PT_render_presets(bpy.types.Panel):
    bl_label = "Render Preset"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        props = context.window_manager.rndrp_properties

        layout = self.layout

        row = layout.row()
        row.template_list(
            "RNDRP_UL_available_presets",
            "",
            props,
            "presets",
            props,
            "active_preset_index",
            rows = 5,
            )

        col = row.column(align=True)
        col.operator("rndrp.reload_presets", icon='FILE_REFRESH', text="")
        col.separator()
        col.operator("rndrp.create_preset", icon='ADD', text="")
        col.operator("rndrp.remove_preset", icon='REMOVE', text="")
        col.separator()
        col.operator("rndrp.modify_preset", icon="GREASEPENCIL", text="")
        col.separator()
        col.operator("rndrp.apply_preset", icon="CHECKMARK", text="")


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_UL_available_presets)
    bpy.utils.register_class(RNDRP_PT_render_presets)

def unregister():
    bpy.utils.unregister_class(RNDRP_UL_available_presets)
    bpy.utils.unregister_class(RNDRP_PT_render_presets)
