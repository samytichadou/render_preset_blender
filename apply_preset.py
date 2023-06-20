import bpy

from . import manage_presets as mp

def set_property_from_entry(entry):
    object = mp.get_object_from_parent_id(entry.parent_name)

    value = entry.value_string
    if entry.value_type=="int":
        value = int(value)
    elif entry.value_type=="bool":
        value = True
        if entry.value_string == "False":
            value = False
    elif entry.value_type=="float":
        value = float(value)

    setattr(object, entry.name, value)

def apply_render_preset(preset):
    for prop in preset.properties:
        set_property_from_entry(prop)

class RNDRP_OT_apply_preset(bpy.types.Operator):
    bl_idname = "rndrp.apply_preset"
    bl_label = "Apply Render Preset"

    preset_name : bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # Check if preset_name is valid
        try:
            preset = context.window_manager.rndrp_properties.presets[self.preset_name]
        except KeyError:
            self.report({'WARNING'}, f"Preset {self.preset_name} not valid")
            return {"CANCELLED"}

        apply_render_preset(preset)

        self.report({'INFO'}, f"Preset {self.preset_name} applied")

        return {'FINISHED'}


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_OT_apply_preset)

def unregister():
    bpy.utils.unregister_class(RNDRP_OT_apply_preset)
