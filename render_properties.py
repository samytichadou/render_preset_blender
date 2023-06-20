render_properties = {}

# render
render_properties["scene.render"] = [
    "resolution_x",
    "resolution_y",
    "resolution_percentage",
    "pixel_aspect_x",
    "pixel_aspect_y",

    "use_border",
    "use_crop_to_border",

    "fps",
    "fps_base",

    "use_file_extension",
    "use_render_cache",

    "use_overwrite",
    "use_placeholder",

    #TODO Metadatas
    ]

# render.image_settings
render_properties["scene.render.image_settings"] = [
    "file_format",
    "color_mode",
    "compression",
    "color_depth",
    #TODO Formats details (video...)
    ]

# Disabled by default
render_properties_disabled = [
    "pixel_aspect_x",
    "pixel_aspect_y",

    "use_border",
    "use_crop_to_border",

    "fps",
    "fps_base",

    "use_render_cache",
    ]
