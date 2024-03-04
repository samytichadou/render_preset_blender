import bpy
import os

addon_name = os.path.basename(os.path.dirname(__file__))

# addon preferences
class RNDRP_PF_addon_prefs(bpy.types.AddonPreferences):
    bl_idname = addon_name

    folder_default = os.environ.get(
        "RENDER_PRESETS_DEFAULT_PATH",
        os.path.join(
            os.path.join(
                bpy.utils.resource_path("USER"),
                "datafiles"
            ), "render_presets"
        )
    )

    preferences_folder: bpy.props.StringProperty(
        name="BPM preferences folder",
        default=folder_default,
        description="Where BPM store global preferences",
        subtype="DIR_PATH",
        )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "preferences_folder", text = "Preference Folder")

# Get addon preferences
def get_addon_preferences():
    addon = bpy.context.preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)

### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_PF_addon_prefs)
def unregister():
    bpy.utils.unregister_class(RNDRP_PF_addon_prefs)
