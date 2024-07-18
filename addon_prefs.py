import bpy, os


# addon preferences
class RNDRP_PF_addon_prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    preferences_folder: bpy.props.StringProperty(
        name="BPM preferences folder",
        default=os.path.join(
            os.path.join(
                bpy.utils.resource_path("USER"),
                "datafiles"
            ),
            "render_presets"
        ),
        description="Where BPM store global preferences",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "preferences_folder", text = "Preference Folder")
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Infos", icon="INFO")
        col.label(text="You can use python command to apply render presets through script :")
        col.separator()
        subbox = col.box()
        subcol = subbox.column(align=True)
        subcol.label(text="With preset name :")
        subcol.label(text='bpy.ops.rndrp.apply_preset_name(preset_name="preset_name")')
        subbox = col.box()
        subcol = subbox.column(align=True)
        subcol.label(text="With preset json filepath :")
        subcol.label(text='bpy.ops.rndrp.apply_preset_json(json_filepath="preset_filepath")')

# Get addon preferences
def get_addon_preferences():
    return bpy.context.preferences.addons[__package__]
    # addon = bpy.context.preferences.addons.get(__package__)
    # return getattr(addon, "preferences", None)

### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_PF_addon_prefs)
def unregister():
    bpy.utils.unregister_class(RNDRP_PF_addon_prefs)
