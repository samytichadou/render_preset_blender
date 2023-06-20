import bpy


class RNDRP_UL_available_presets(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "name", text="", emboss=False)


# main panel
class RNDRP_PT_render_presets(bpy.types.Panel):
    bl_label = "Render Presets"
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
            rows = 4,
            )

        col = row.column(align=True)
        col.operator("rndrp.reload_presets", icon='FILE_REFRESH', text="")
        col.separator()
        col.operator("rndrp.create_preset", icon='ADD', text="")

        sub = col.column(align=True)
        op1 = sub.operator("rndrp.remove_preset", icon='REMOVE', text="")
        sub.separator()
        op2 = sub.operator("rndrp.apply_preset", icon="CHECKMARK", text="")

        # Deal with active preset or not
        if props.active_preset_index in range(0,len(props.presets)):
            active_preset = props.presets[props.active_preset_index]
            op1.preset_name = active_preset.name
            op2.preset_name = active_preset.name
        else:
            sub.enabled = False


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_UL_available_presets)
    bpy.utils.register_class(RNDRP_PT_render_presets)

def unregister():
    bpy.utils.unregister_class(RNDRP_UL_available_presets)
    bpy.utils.unregister_class(RNDRP_PT_render_presets)
