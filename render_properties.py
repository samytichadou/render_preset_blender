# This file lists render properties categories
# and properties to avoid or enable by default


# Categories to look for render properties
render_properties = [
    "scene.render",
    "scene.render.image_settings",
    "scene.cycles",
    "scene.eevee",
    "scene.view_settings",
    "scene.grease_pencil_settings",
    "scene.cgru",
    ]

# Properties to avoid
render_properties_avoided = [
    # scene.cgru
    "adv_options",
    ]

# Enabled by default
render_properties_enabled = [
    # scene.render
    "engine",
    "resolution_x",
    "resolution_y",
    "resolution_percentage",
    "use_file_extension",
    "use_overwrite",
    "use_placeholder",
    "use_simplify",
    "use_stamp",
    "use_stamp_date",
    "use_stamp_time",
    "use_stamp_render_time",
    "use_stamp_frame",
    "use_stamp_memory",
    "use_stamp_hostname",
    "use_stamp_filename",
    "film_transparent",
    "use_freestyle",

    # scene.render.image_settings
    "file_format",
    "color_mode",
    "compression",
    "color_depth",
    "quality",

    # scene.cycles
    "device",
    "feature_set",
    "dicing_rate",
    "use_denoising",
    "denoiser",
    "use_auto_tile",
    "tile_size",
    "caustics_reflective",
    "caustics_refractive",
    "samples",

    # scene.eevee
    "aa_render_samples",
    "use_taa_reprojection",
    "use_gtao",
    "sss_samples",
    "use_overscan",
    "overscan_size",

    # scene.view_settings
    "view_transform",
    "look",

    # scene.grease_pencil_settings
    "antialias_threshold",

    # scene.cgru
    "fpertask",
    "priority",
    ]
