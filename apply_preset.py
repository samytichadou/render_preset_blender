import bpy, os

from . import manage_presets as mp


def format_value_type(entry):
    value = None
    if entry.value_type in ["str", "enum"]:
        value = entry.value_string
    elif entry.value_type == "int":
        value = entry.value_integer
    elif entry.value_type == "float":
        value = entry.value_float
    elif entry.value_type == "bool":
        value = entry.value_boolean

    return value

def format_value_type_dict(dictionnary):
    value = None
    if dictionnary["value_type"] in ["str", "enum"]:
        value = dictionnary["value_string"]
    elif dictionnary["value_type"] == "int":
        value = dictionnary["value_integer"]
    elif dictionnary["value_type"] == "float":
        value = dictionnary["value_float"]
    elif dictionnary["value_type"] == "bool":
        value = dictionnary["value_boolean"]

    return value

def set_property_from_entry(entry):
    object = mp.get_object_from_parent_id(entry.parent_name)

    value = format_value_type(entry)

    try:
        setattr(object, entry.identifier, value)
    except AttributeError:
        print(f"Render Presets --- Unable to set {entry.parent_name}.{entry.identifier}")
        return False

    return True

def set_property_from_json_entry(entry):
    object = mp.get_object_from_parent_id(entry["parent_name"])
    
    value = format_value_type_dict(entry)

    try:
        setattr(object, entry["identifier"], value)
    except AttributeError:
        parent = entry["parent_name"]
        identifier = entry["identifier"]
        print(f"Render Presets --- Unable to set {parent}.{identifier}")
        return False

    return True
        

def apply_render_preset(preset):
    check_missing = False
    for prop in preset.properties:
        if not set_property_from_entry(prop):
            check_missing = True
    return not check_missing

def apply_render_json(json_filepath):
    datas = mp.read_json(json_filepath)
    
    check_missing = False
    for prop in datas["properties"]:
        if not set_property_from_json_entry(prop):
            check_missing = True
    return not check_missing
        

class RNDRP_OT_apply_preset(bpy.types.Operator):
    bl_idname = "rndrp.apply_preset"
    bl_label = "Apply Render Preset"
    bl_options = {"INTERNAL", "UNDO"}
    bl_description = "Apply selected preset from interface"

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
    
    
class RNDRP_OT_apply_preset_name(bpy.types.Operator):
    bl_idname = "rndrp.apply_preset_name"
    bl_label = "Apply Render Preset Name"
    bl_options = {"INTERNAL", "UNDO"}
    bl_description = "Apply preset from name"
    
    preset_name : bpy.props.StringProperty()
    preset = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        mp.reload_presets()
        
        # Check if preset name exists
        if not self.preset_name:
            self.report({'WARNING'}, "Preset name missing")
            return {"CANCELLED"}

        # Check if preset is valid
        props = context.window_manager.rndrp_properties
        try:
            self.preset = props.presets[self.preset_name]
        except KeyError:
            self.report({'WARNING'}, "Preset not valid")
            return {"CANCELLED"}

        if not apply_render_preset(self.preset):
            self.report({'WARNING'}, f"Preset : {self.preset.name} applied with missing properties, see console")
        else:
            self.report({'INFO'}, f"Preset : {self.preset.name} applied")

        return {'FINISHED'}
    
    
class RNDRP_OT_apply_preset_json(bpy.types.Operator):
    bl_idname = "rndrp.apply_preset_json"
    bl_label = "Apply Render Preset json"
    bl_options = {"INTERNAL", "UNDO"}
    bl_description = "Apply json preset filepath"

    json_filepath : bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # Check if preset json exists
        if not os.path.isfile(self.json_filepath):
            self.report({'WARNING'}, "Preset json does not exist")
            return {"CANCELLED"}

        if not apply_render_json(self.json_filepath):
            self.report({'WARNING'}, f"Preset : {self.json_filepath} applied with missing properties, see console")
        else:
            self.report({'INFO'}, f"Preset : {self.json_filepath} applied")

        return {'FINISHED'}


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_OT_apply_preset)
    bpy.utils.register_class(RNDRP_OT_apply_preset_name)
    bpy.utils.register_class(RNDRP_OT_apply_preset_json)

def unregister():
    bpy.utils.unregister_class(RNDRP_OT_apply_preset)
    bpy.utils.unregister_class(RNDRP_OT_apply_preset_name)
    bpy.utils.unregister_class(RNDRP_OT_apply_preset_json)
