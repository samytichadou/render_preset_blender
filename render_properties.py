render_properties = {}

# scene.render
render_properties["scene.render"] = [
    "engine",

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

    "use_simplify",

    "use_stamp",
    "use_stamp_date",
    "use_stamp_time",
    "use_stamp_render_time",
    "use_stamp_frame",
    "use_stamp_frame_range",
    "use_stamp_memory",
    "use_stamp_hostname",
    "use_stamp_camera",
    "use_stamp_lens",
    "use_stamp_scene",
    "use_stamp_marker",
    "use_stamp_filename",
    "use_stamp_sequencer_strip",

    "film_transparent",
    ]

# scene.render.image_settings
render_properties["scene.render.image_settings"] = [
    "file_format",
    "color_mode",
    "compression",
    "color_depth",
    "quality",
    #TODO Formats details (video...)
    ]

# scene.cycles
render_properties["scene.cycles"] = [
    "device",
    "feature_set",

    "dicing_rate",

    "use_denoising",
    "denoiser",
    "adaptive_threshold",

    "use_auto_tile",
    "tile_size",

    "caustics_reflective",
    "caustics_refractive",

    "samples"
    ]

# scene.eevee
render_properties["scene.eevee"] = [
    "taa_render_sample",
    "use_taa_reprojection",

    "use_gtao",
    "gtao_distance",
    "gtao_factor",
    "gtao_quality",
    "use_gtao_bent_normals",
    "use_gtao_bounce",
    ]

# scene.view_settings
render_properties["scene.view_settings"] = [
    "view_transform",
    ]

# scene.cgru
render_properties["scene.cgru"] = [
    "fpertask",
    "priority",
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
