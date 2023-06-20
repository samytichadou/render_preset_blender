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

        row = layout.row(align=True)
        row.operator("rndrp.reload_presets")
        row.operator("rndrp.create_preset")

        # If active preset
        if props.active_preset_index in range(0,len(props.presets)):
            active_preset = props.presets[props.active_preset_index]
            op = row.operator("rndrp.apply_preset")
            op.preset_name = active_preset.name

        row = layout.row()
        row.template_list(
            "RNDRP_UL_available_presets",
            "",
            props,
            "presets",
            props,
            "active_preset_index",
            rows = 3,
            )


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_UL_available_presets)
    bpy.utils.register_class(RNDRP_PT_render_presets)

def unregister():
    bpy.utils.unregister_class(RNDRP_UL_available_presets)
    bpy.utils.unregister_class(RNDRP_PT_render_presets)
