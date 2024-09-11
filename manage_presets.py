import bpy, os, json

from bpy.app.handlers import persistent

from .addon_prefs import get_addon_preferences
from . import render_properties as rp

# TODO Better popup ui panels
# TODO Warn user if preset name already exists
# TODO Use min max

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

def get_enum_values(object, identifier):
    # Correct way
    
    # values = []
    # prop = object.bl_rna.properties[identifier]
    
    # try:
    #     for e in prop.enum_items:
    #         values.append(e.identifier)
    # except AttributeError:
    #     pass
    # return values
    
    # Hacky way
    try:
        setattr(object, identifier, "")
    except Exception as e:
        return str(e).split("'")[1::2]

    return []


def enum_callback(self, context):
    items = []
    
    if not self.parent_name or not self.identifier:
        return items

    object = get_object_from_parent_id(self.parent_name)
    values = get_enum_values(object, self.identifier)

    if values:
        for v in values:
            items.append((v, v, ""))
    
    return items

class RNDRP_PR_render_properties_enum(bpy.types.PropertyGroup):
    """A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
    identifier : bpy.props.StringProperty()
    parent_name : bpy.props.StringProperty()
    
    enum_values : bpy.props.EnumProperty(
        name = "Enum Property",
        items = enum_callback,
        )

class RNDRP_PR_render_properties(bpy.types.PropertyGroup):
    """A bpy.types.PropertyGroup descendant for bpy.props.CollectionProperty"""
    enabled : bpy.props.BoolProperty()

    identifier : bpy.props.StringProperty()

    value_string : bpy.props.StringProperty()
    value_boolean : bpy.props.BoolProperty()
    value_integer : bpy.props.IntProperty()
    value_float : bpy.props.FloatProperty()

    value_min : bpy.props.FloatProperty()
    value_max : bpy.props.FloatProperty()

    value_type : bpy.props.StringProperty()
    parent_name : bpy.props.StringProperty()
    
    enum : bpy.props.CollectionProperty(
        type=RNDRP_PR_render_properties_enum,
        )

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
        try:
            object = getattr(object, p)
        except AttributeError:
            # print(f"Render Preset --- Unable to get {parent_name}")
            return None
    return object

def get_value_from_parent_key(parent_name, key):
    object = get_object_from_parent_id(parent_name)
    if object is None:
        return None
    return getattr(object, key)

def category_items_callback(self, context):
    items = []
    for k in rp.render_properties:
        # Test if cat exists
        if get_object_from_parent_id(k) is not None:
            items.append((k, k, ""))
    
    return items

def get_render_properties(collection_property, disable_prop=False):
    collection_property.clear()
    for cat in rp.render_properties:
        parent = get_object_from_parent_id(cat)
        if parent is None:
            print(f"Render Preset --- {cat} missing, properties ignored")
            continue
        for identifier, prop in parent.rna_type.properties.items():
            value = get_value_from_parent_key(cat, identifier)
            if value is not None\
            and identifier not in rp.render_properties_avoided\
            and type(value).__name__ in {"int","str","float","bool"}:
                new = collection_property.add()
                new.identifier = identifier
                new.name = prop.name
                new.parent_name = cat
                new.value_type = type(value).__name__

                if len(get_enum_values(parent, identifier)) !=0:
                    
                    new_enum = new.enum.add()
                    new_enum.identifier = identifier
                    new_enum.parent_name = cat
                    
                    # Set enum value
                    # Handle problematic enum properties (engine...)
                    try:
                        object = get_object_from_parent_id(cat)
                        new.enum[0].enum_values = getattr(object, identifier)
                        new.value_type = "enum"
                    except TypeError:
                        print(f"Render Preset --- Unable to set enum property : \
                                {cat}.{identifier} - {value}, converting to string")
                        new.enum.clear()

                if type(value) is str:
                    new.value_string = value
                elif type(value) is int:
                    new.value_integer = value
                    new.value_min = prop.hard_min
                    new.value_max = prop.hard_max
                elif type(value) is float:
                    new.value_float = value
                    new.value_min = prop.hard_min
                    new.value_max = prop.hard_max
                elif type(value) is bool:
                    new.value_boolean = value

                if not disable_prop and identifier in rp.render_properties_enabled:
                    new.enabled = True

def get_dataset_from_collection(name, collection_property):
    dataset = {}
    dataset["name"] = name
    dataset["properties"] = []
    for entry in collection_property:
        if entry.enabled:
            propdatas = {}
            propdatas["name"] = entry.name
            propdatas["identifier"] = entry.identifier

            propdatas["value_string"] = entry.value_string
            propdatas["value_integer"] = entry.value_integer
            propdatas["value_float"] = entry.value_float
            propdatas["value_boolean"] = entry.value_boolean

            propdatas["value_min"] = entry.value_min
            propdatas["value_max"] = entry.value_max

            propdatas["value_type"] = entry.value_type
            propdatas["parent_name"] = entry.parent_name
            dataset["properties"].append(propdatas)
            
            # Enum
            if entry.enum:
                propdatas["value_type"] = "enum"
                propdatas["value_string"] = entry.enum[0].enum_values

    return dataset

def check_preset_name_exists(name):
    try:
        bpy.context.window_manager.rndrp_properties.presets[name]
        return True
    except KeyError:
        return False
    
def get_unique_preset_name(name):
    
    if check_preset_name_exists(name):
        
        cnt = 0
        
        while True:
            
            if cnt < 1000:
                preset_name = f"{name}_{str(cnt).zfill(3)}"
            else:
                preset_name = f"{name}_{str(cnt)}"
                
            if not check_preset_name_exists(preset_name):
                name = preset_name
                break
            
            cnt += 1
            
    return name

def remove_number_ending(name):

    if name[-3:].isdigit()\
    and name[-4:][:1] == "_":
        name = name[:-4]

    return name
    
def draw_property(prop, container):
    row = container.row(align=True)
    row.prop(prop, "enabled", text=prop.name)
    
    if prop.enum:
        row.prop(prop.enum[0], "enum_values", text="")
    elif prop.value_type == "str":
        row.prop(prop, "value_string", text="")
    elif prop.value_type == "int":
        row.prop(prop, "value_integer", text="")
    elif prop.value_type == "float":
        row.prop(prop, "value_float", text="")
    elif prop.value_type == "bool":
        row.prop(prop, "value_boolean", text="")


# Common class
class RNDRP_OT_preset_management(bpy.types.Operator):
    
    # Properties
    render_properties : bpy.props.CollectionProperty(
        type=RNDRP_PR_render_properties,
        )
    categories : bpy.props.EnumProperty(
        name = "Categories",
        description = "Categories to get properties from",
        items = category_items_callback,
        )
    preset_name : bpy.props.StringProperty(
        name = "Preset Name",
        default = "New Preset",
        # options = {"SKIP_SAVE"},
        )
    show_all_properties : bpy.props.BoolProperty(
        name = "Show Unsaved Properties",
        description = "Show unsaved properties to enable them for this preset",
        )
    search_property : bpy.props.StringProperty(
        name = "Search",
        options = {"TEXTEDIT_UPDATE"},
        description = "Search property in all categories",
        )
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "preset_name", text="Name")
        
        # if check_preset_name_exists(self.preset_name):
        #     row.label(text="", icon="ERROR")

        box = layout.box()
        col = box.column()
        col.label(text="Filters")
        subcol = col.column()
        subcol .enabled = not self.search_property
        subcol .prop(self, "show_all_properties")
        subcol .prop(self, "categories")
        col.prop(self, "search_property", icon="VIEWZOOM")

        layout.separator()

        col = layout.column(align=True)

        row = col.row()
        row.label(text="Save Property")
        sub = row.row()
        sub.alignment="RIGHT"
        sub.label(text="Property Value")

        col.separator()

        chk_missing = True
        
        for prop in self.render_properties:
            
            # Search field
            if self.search_property:
                
                if self.search_property.lower() in prop.identifier\
                or self.search_property.lower() in prop.name.lower():
                    
                    chk_missing = False
                    draw_property(prop, col)
                    
            # No search field
            elif prop.parent_name == self.categories:
                
                if self.show_all_properties or prop.enabled:
                    
                    chk_missing = False
                    draw_property(prop, col)

        if chk_missing:
            if self.search_property:
                col.label(text=f"No matching Property")
            else:
                col.label(text=f"Missing Attribute : {self.categories}")


class RNDRP_OT_create_render_preset(RNDRP_OT_preset_management):
# class RNDRP_OT_create_render_preset(bpy.types.Operator):
    bl_idname = "rndrp.create_preset"
    bl_label = "Create Render Preset"

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        # Reload presets
        reload_presets()

        # Update of props
        get_render_properties(self.render_properties)
        
        # Remove "_xxx" ending
        self.preset_name = remove_number_ending(self.preset_name)
        # Get unique name
        unique_name = get_unique_preset_name(self.preset_name)
        self.preset_name = unique_name

        return context.window_manager.invoke_props_dialog(self)#, width=400)

    def execute(self, context):
        folder = get_preset_folder()

        # Check for valid folder
        if not os.path.isdir(folder):
            self.report({'WARNING'}, "Invalid Preset Folder, check addon preferences")
            return {"CANCELLED"}

        filepath = os.path.join(folder, f"{self.preset_name}.json")

        # Check if preset already exists
        if os.path.isfile(filepath):
            self.report({'WARNING'}, f"{self.preset_name} already exists, choose a different name")
            return {"CANCELLED"}

        dataset = get_dataset_from_collection(
            self.preset_name,
            self.render_properties,
            )
        write_json_file(dataset, filepath)

        reload_presets()

        # Refresh UI
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, f"{self.preset_name} preset created")

        return {'FINISHED'}


def get_render_properties_from_preset(collection, preset):
    for prop in preset.properties:
        
        new_prop = None
        try:
            # If prop already exists
            new_prop = collection[prop.name]
        except KeyError:
            new_prop = collection.add()
            new_prop.name = prop.name
            new_prop.identifier = prop.identifier
            new_prop.parent_name = prop.parent_name
            new_prop.value_type = prop.value_type

        new_prop.value_string = prop.value_string
        new_prop.value_integer = prop.value_integer
        new_prop.value_float = prop.value_float
        new_prop.value_boolean = prop.value_boolean

        new_prop.value_min = prop.value_min
        new_prop.value_max = prop.value_max

        new_prop.enabled = True
        
        # Enum
        if len(prop.enum) != 0:
            new_enum = new_prop.enum.add()
            new_enum.identifier = prop.identifier
            new_enum.parent_name = prop.parent_name

            try:
                # new_enum.enum_values = prop.value_string
                new_prop.enum[0].enum_values = prop.value_string
            except:
                print(f"Render Preset --- Unable to set enum property : \
                        {prop.parent_name}.{prop.identifier} - {prop.value_string}, converting to string")
                new_prop.enum.clear()

def modify_category_items_callback(scene, context):
    cat = []
    items = []

    for k in rp.render_properties:
        cat.append(k)

    props = context.window_manager.rndrp_properties
    preset = props.presets[props.active_preset_index]
    for prop in preset.properties:
        if prop.parent_name not in cat:
            cat.append(prop.parent_name)

    for prop in cat:
        items.append((prop, prop, ""))

    return items

def check_active_preset():
    props = bpy.context.window_manager.rndrp_properties
    return props.active_preset_index in range(0,len(props.presets))


class RNDRP_OT_modify_render_preset(RNDRP_OT_preset_management):
    bl_idname = "rndrp.modify_preset"
    bl_label = "Modify Render Preset"

    preset = None

    @classmethod
    def poll(cls, context):
        return check_active_preset()

    def invoke(self, context, event):
        # Check for valid folder
        folder = get_preset_folder()
        if not os.path.isdir(folder):
            self.report({'WARNING'}, "Invalid Preset Folder, check addon preferences")
            return {'CANCELLED'}

        # Check if preset_name is valid
        props = context.window_manager.rndrp_properties
        try:
            self.preset = props.presets[props.active_preset_index]
        except KeyError:
            self.report({'WARNING'}, "Preset not valid")
            return {'CANCELLED'}

        # Check if preset file exists
        filepath = os.path.join(folder, f"{self.preset.name}.json")
        if not os.path.isfile(filepath):
            self.report({'WARNING'}, "Invalid Preset File")
            return {'CANCELLED'}

        self.preset_name = self.preset.name

        reload_presets()

        # Update of props
        get_render_properties(self.render_properties, disable_prop = True)
        # Get props from existing preset
        get_render_properties_from_preset(self.render_properties, self.preset)

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        # Check for existing preset name
        if check_preset_name_exists(self.preset_name)\
        and self.preset_name != self.preset.name:
            self.report({'WARNING'}, f"{self.preset_name} already exists, choose a different name")
            return {'CANCELLED'}

        folder = get_preset_folder()

        filepath = os.path.join(folder, f"{self.preset.name}.json")

        dataset = get_dataset_from_collection(
            self.preset_name,
            self.render_properties,
            )

        # Remove old file if needed
        if self.preset.name != self.preset_name:
            os.remove(filepath)
            filepath = os.path.join(folder, f"{self.preset_name}.json"
                                    )
        write_json_file(dataset, filepath)

        reload_presets()

        # Refresh UI
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, f"{self.preset_name} preset modified")

        return {'FINISHED'}


class RNDRP_OT_reload_presets(bpy.types.Operator):
    bl_idname = "rndrp.reload_presets"
    bl_label = "Reload Render Presets"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        reload_presets()

        # Refresh UI
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "Presets reloaded")

        return {'FINISHED'}


def clear_preset_collection():
    coll = bpy.context.window_manager.rndrp_properties.presets
    coll.clear()

def load_preset_datas(dataset):
    coll = bpy.context.window_manager.rndrp_properties.presets
    new = coll.add()
    new.name = dataset["name"]

    for prop in dataset["properties"]:
        new_prop = new.properties.add()
        new_prop.name = prop["name"]
        new_prop.identifier = prop["identifier"]

        new_prop.value_string = prop["value_string"]
        new_prop.value_integer = prop["value_integer"]
        new_prop.value_float = prop["value_float"]
        new_prop.value_boolean= prop["value_boolean"]

        new_prop.value_min = prop["value_min"]
        new_prop.value_max = prop["value_max"]

        new_prop.value_type = prop["value_type"]
        new_prop.parent_name = prop["parent_name"]
        
        # Enum
        if prop["value_type"] == "enum":
            new_enum = new_prop.enum.add()
            new_enum.identifier = prop["identifier"]
            new_enum.parent_name = prop["parent_name"]

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

def remove_preset(collection, preset_name):
    index = collection.presets.find(preset_name)

    # Remove preset file
    filepath = os.path.join(get_preset_folder(), f"{preset_name}.json")
    if os.path.isfile(filepath):
        os.remove(filepath)

    # Remove preset entry
    collection.presets.remove(index)
    if collection.active_preset_index == index\
    and index > 0:
        collection.active_preset_index -= 1


class RNDRP_OT_remove_preset(bpy.types.Operator):
    bl_idname = "rndrp.remove_preset"
    bl_label = "Remove Render Preset"
    bl_options = {"INTERNAL"}

    preset_name : bpy.props.StringProperty()
    preset = None

    @classmethod
    def poll(cls, context):
        return check_active_preset()

    def invoke(self, context, event):
        reload_presets()

        # Check if preset_name is valid
        props = context.window_manager.rndrp_properties
        try:
            self.preset = props.presets[props.active_preset_index]
        except KeyError:
            self.report({'WARNING'}, "Preset not valid")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Removing : {self.preset.name}")
        layout.label(text="Are you sure ?")

    def execute(self, context):
        props = context.window_manager.rndrp_properties
        remove_preset(props, self.preset.name)

        # Refresh UI
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, f"Preset {self.preset.name} removed")

        return {'FINISHED'}


@persistent
def reload_preset_startup(scene):
    print("Render Preset --- Startup handler")
    reload_presets()


### REGISTER ---
def register():
    bpy.utils.register_class(RNDRP_PR_render_properties_enum)
    bpy.utils.register_class(RNDRP_PR_render_properties)
    bpy.utils.register_class(RNDRP_OT_create_render_preset)
    bpy.utils.register_class(RNDRP_OT_modify_render_preset)
    bpy.utils.register_class(RNDRP_PR_preset_collection)
    bpy.utils.register_class(RNDRP_PR_general_properties)
    bpy.utils.register_class(RNDRP_OT_reload_presets)
    bpy.utils.register_class(RNDRP_OT_remove_preset)
    bpy.types.WindowManager.rndrp_properties = \
        bpy.props.PointerProperty(
            type = RNDRP_PR_general_properties,
            name="Render Presets Properties",
            )
    bpy.app.handlers.load_post.append(reload_preset_startup)

def unregister():
    bpy.utils.unregister_class(RNDRP_PR_render_properties_enum)
    bpy.utils.unregister_class(RNDRP_PR_render_properties)
    bpy.utils.unregister_class(RNDRP_OT_create_render_preset)
    bpy.utils.unregister_class(RNDRP_OT_modify_render_preset)
    bpy.utils.unregister_class(RNDRP_PR_preset_collection)
    bpy.utils.unregister_class(RNDRP_PR_general_properties)
    bpy.utils.unregister_class(RNDRP_OT_reload_presets)
    bpy.utils.unregister_class(RNDRP_OT_remove_preset)
    del bpy.types.WindowManager.rndrp_properties
    bpy.app.handlers.load_post.remove(reload_preset_startup)
