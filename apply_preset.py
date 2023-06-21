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

    try:
        setattr(object, entry.name, value)
    except AttributeError:
        print(f"Render Presets --- Unable to set {entry.parent_name}.{entry.name}")
        return False

    return True

def apply_render_preset(preset):
    check_missing = False
    for prop in preset.properties:
        if not set_property_from_entry(prop):
            check_missing = True
    return not check_missing

class RNDRP_OT_apply_preset(bpy.types.Operator):
    bl_idname = "rndrp.apply_preset"
    bl_label = "Apply Render Preset"
    bl_options = {"INTERNAL", "UNDO"}

    preset = None

    @classmethod
    def poll(cls, context):
        return mp.check_active_preset()

    def execute(self, context):
        mp.reload_presets()

        # Check if preset_name is valid
        props = context.window_manager.rndrp_properties
        try:
            self.preset = props.presets[props.active_preset_index]
        except KeyError:
            self.report({'WARNING'}, "Preset not valid")
            return {"CANCELLED"}

        if not apply_render_preset(self.preset):
            self.report({'WARNING'}, f"Preset : {self.preset.name} applied with missing properties, see console")
        else:
            self.report({'INFO'}, f"Preset : {self.preset.name} applied")

        return {'FINISHED'}


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_OT_apply_preset)

def unregister():
    bpy.utils.unregister_class(RNDRP_OT_apply_preset)
