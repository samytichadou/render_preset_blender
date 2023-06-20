import bpy
from bpy.app.handlers import persistent

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


class RNDRP_PR_render_properties(bpy.types.PropertyGroup):
    """A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
    enabled : bpy.props.BoolProperty(default=True)
    value_string : bpy.props.StringProperty()
    value_type : bpy.props.StringProperty()
    parent_name : bpy.props.StringProperty()

class RNDRP_PR_preset_collection(bpy.types.PropertyGroup):
    properties : bpy.props.CollectionProperty(
        type=RNDRP_PR_render_properties,
        )

class RNDRP_PR_general_properties(bpy.types.PropertyGroup):
    presets : bpy.props.CollectionProperty(
        type=RNDRP_PR_preset_collection,
        )
    active_preset_index : bpy.props.IntProperty()


def get_object_from_parent_id(parent_name):
    parents = parent_name.split(".")
    object = bpy.context
    for p in parents:
        object = getattr(object, p)
    return object

def get_value_from_parent_key(parent_name, key):
    return getattr(get_object_from_parent_id(parent_name), key)

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
            value = get_value_from_parent_key(cat, prop)
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

def check_preset_name_exists(name):
    try:
        bpy.context.window_manager.rndrp_properties.presets[name]
        return True
    except KeyError:
        return False

class RNDRP_OT_create_render_preset(bpy.types.Operator):
    bl_idname = "rndrp.create_preset"
    bl_label = "Create Render Preset"

    render_properties : bpy.props.CollectionProperty(
        type=RNDRP_PR_render_properties,
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
        return True

    def invoke(self, context, event):
        # Reload presets
        reload_presets()
        # Update of props
        get_render_properties(self.render_properties)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "preset_name")
        if check_preset_name_exists(self.preset_name):
            row.label(text="", icon="ERROR")

        layout.prop(self, "categories", text="")
        col = layout.column(align=True)

        for prop in self.render_properties:
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
            self.render_properties,
            )
        write_json_file(dataset, filepath)

        reload_presets()

        self.report({'INFO'}, f"{self.preset_name} preset created")

        return {'FINISHED'}


def clear_preset_collection():
    coll = bpy.context.window_manager.rndrp_properties.presets
    coll.clear()

def load_preset_datas(dataset):
    coll = bpy.context.window_manager.rndrp_properties.presets
    new = coll.add()
    new.name = dataset["name"]

    for prop in dataset["properties"]:
        newprop = new.properties.add()
        newprop.name = prop["name"]
        newprop.value_string = prop["value_string"]
        newprop.value_type = prop["value_type"]
        newprop.parent_name = prop["parent_name"]

def reload_presets():
    print("Render Preset --- Reloading presets")

    # Clear preset collection
    clear_preset_collection()

    folder = get_preset_folder()
    for f in os.listdir(folder):
        filepath = os.path.join(folder, f)
        dataset = read_json(filepath)
        load_preset_datas(dataset)
        print(f"Render Preset --- Loaded : {filepath}")

    print("Render Preset --- Presets reloaded")

class RNDRP_OT_reload_presets(bpy.types.Operator):
    bl_idname = "rndrp.reload_presets"
    bl_label = "Reload Render Presets"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        reload_presets()
        self.report({'INFO'}, "Presets reloaded")

        return {'FINISHED'}

@persistent
def reload_preset_startup(scene):
    print("Render Preset --- Startup handler")
    reload_presets()


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_PR_render_properties)
    bpy.utils.register_class(RNDRP_OT_create_render_preset)
    bpy.utils.register_class(RNDRP_PR_preset_collection)
    bpy.utils.register_class(RNDRP_PR_general_properties)
    bpy.utils.register_class(RNDRP_OT_reload_presets)
    bpy.types.WindowManager.rndrp_properties = \
        bpy.props.PointerProperty(
            type = RNDRP_PR_general_properties,
            name="Render Presets Properties",
            )
    bpy.app.handlers.load_post.append(reload_preset_startup)

def unregister():
    bpy.utils.unregister_class(RNDRP_PR_render_properties)
    bpy.utils.unregister_class(RNDRP_OT_create_render_preset)
    bpy.utils.unregister_class(RNDRP_PR_preset_collection)
    bpy.utils.unregister_class(RNDRP_PR_general_properties)
    bpy.utils.unregister_class(RNDRP_OT_reload_presets)
    del bpy.types.WindowManager.rndrp_properties
    bpy.app.handlers.load_post.remove(reload_preset_startup)
