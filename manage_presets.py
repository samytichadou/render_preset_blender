import bpy
import os
import json

from .addon_prefs import get_addon_preferences
from . import render_properties as rp


def read_json(filepath):
    with open(filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset

def write_json_file(datas, path) :
    with open(path, "w") as write_file :
        json.dump(datas, write_file, indent=4, sort_keys=False)

def get_preset_folder():
    folder = bpy.path.abspath(get_addon_preferences().preferences_folder)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder

def get_value_from_parent_id(parent_name, key):
    parents = parent_name.split(".")
    base_attr = bpy.context
    for p in parents:
        base_attr = getattr(base_attr, p)
    return getattr(base_attr, key)

class RNDRP_PR_TemporaryProperties(bpy.types.PropertyGroup):
    """A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
    enabled : bpy.props.BoolProperty(default=True)
    value_string : bpy.props.StringProperty()
    value_type : bpy.props.StringProperty()
    parent_name : bpy.props.StringProperty()

def category_items_callback(scene, context):
    items = []
    for k in rp.render_properties:
        items.append((k, k, ""))
    return items

def get_render_properties(collection_property):
    collection_property.clear()
    for cat in rp.render_properties:
        for prop in rp.render_properties[cat]:
            new = collection_property.add()
            new.name = prop
            new.parent_name = cat
            value = get_value_from_parent_id(cat, prop)
            new.value_string = str(value)
            new.value_type = type(value).__name__
            if prop in rp.render_properties_disabled:
                new.enabled = False

def get_dataset_from_collection(name, collection_property):
    dataset = {}
    dataset["name"] = name
    dataset["properties"] = []
    for entry in collection_property:
        if entry.enabled:
            propdatas = {}
            propdatas["name"] = entry.name
            propdatas["value_string"] = entry.value_string
            propdatas["value_type"] = entry.value_type
            propdatas["parent_name"] = entry.parent_name
            dataset["properties"].append(propdatas)
    return dataset


class RNDRP_OT_create_render_preset(bpy.types.Operator):
    bl_idname = "rndrp.create_render_preset"
    bl_label = "Create Render Preset"

    collection : bpy.props.CollectionProperty(
        type=RNDRP_PR_TemporaryProperties,
        )
    categories : bpy.props.EnumProperty(
        items = category_items_callback,
        )
    preset_name : bpy.props.StringProperty(
        name = "Preset Name",
        default = "New Preset",
        )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        # Update of props
        get_render_properties(self.collection)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        #TODO Check if name already exists and show warning
        layout.prop(self, "categories", text="")
        col = layout.column(align=True)
        for prop in self.collection:
            if prop.parent_name == self.categories:
                row = col.row(align=True)
                row.prop(prop, "enabled", text="")
                row.label(text=prop.name)
                row.prop(prop, "value_string", text="")
                row.separator()
                row.label(text=prop.value_type)

    def execute(self, context):
        folder = get_preset_folder()

        # Check for valid folder
        if not os.path.isdir(folder):
            self.report({'WARNING'}, "Invalid Preset Folder, check addon preferences")
            return {"CANCELLED"}

        filepath = os.path.join(folder, f"{self.preset_name}.json")

        # Check if preset already exists
        if os.path.isfile(filepath):
            self.report({'WARNING'}, "Preset already exists")
            return {"CANCELLED"}

        dataset = get_dataset_from_collection(
            self.preset_name,
            self.collection,
            )
        write_json_file(dataset, filepath)

        self.report({'INFO'}, f"{self.preset_name} preset created")

        return {'FINISHED'}

### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_PR_TemporaryProperties)
    bpy.utils.register_class(RNDRP_OT_create_render_preset)
def unregister():
    bpy.utils.unregister_class(RNDRP_PR_TemporaryProperties)
    bpy.utils.unregister_class(RNDRP_OT_create_render_preset)
