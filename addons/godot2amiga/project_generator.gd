@tool
extends RefCounted

const FORMAT_VERSION := "0.1.0"
const GENERATOR_VERSION := "0.2.0"

const REQUIRED_DIRECTORIES := [
    "scenes",
    "assets",
    "scripts",
    "resources",
    "metadata",
    "diagnostics",
]


func generate(output_directory: String) -> Error:
    var absolute_output := ProjectSettings.globalize_path(output_directory)
    var directory_error := DirAccess.make_dir_recursive_absolute(absolute_output)
    if directory_error != OK:
        push_error(
            "Godot2Amiga: could not create output directory '%s' (error %d)."
            % [output_directory, directory_error]
        )
        return directory_error

    for directory_name: String in REQUIRED_DIRECTORIES:
        var child_error := DirAccess.make_dir_recursive_absolute(
            ProjectSettings.globalize_path(output_directory.path_join(directory_name))
        )
        if child_error != OK:
            push_error(
                "Godot2Amiga: could not create '%s' (error %d)."
                % [directory_name, child_error]
            )
            return child_error

    var project_name := str(
        ProjectSettings.get_setting("application/config/name", "Unnamed project")
    )
    var main_scene_resource := str(
        ProjectSettings.get_setting("application/run/main_scene", "")
    )
    var scene_id := _scene_id_from_path(main_scene_resource)
    var scene_output_path := "scenes/%s.json" % scene_id

    var godot_version_info := Engine.get_version_info()
    var godot_version := "%d.%d.%d" % [
        int(godot_version_info.get("major", 0)),
        int(godot_version_info.get("minor", 0)),
        int(godot_version_info.get("patch", 0)),
    ]

    var manifest := {
        "$schema": "https://godot2amiga.org/schemas/g2a/manifest.schema.json",
        "format": "g2a",
        "format_version": FORMAT_VERSION,
        "generator": {
            "name": "Godot2Amiga",
            "version": GENERATOR_VERSION,
            "godot_version": godot_version,
        },
    }

    var project := {
        "$schema": "https://godot2amiga.org/schemas/g2a/project.schema.json",
        "id": _slugify(project_name),
        "name": project_name,
        "main_scene": scene_output_path,
        "source": {
            "engine": "godot",
            "project_file": "res://project.godot",
            "main_scene": main_scene_resource,
        },
    }

    var export_profile := {
        "$schema": "https://godot2amiga.org/schemas/g2a/export-profile.schema.json",
        "id": "amiga500-ocs-pal",
        "machine": "Amiga 500",
        "chipset": "OCS",
        "cpu": "68000",
        "video_standard": "PAL",
        "chip_ram_kib": 512,
        "fast_ram_kib": 0,
        "runtime": "ACE",
    }

    var scene_document := {
        "$schema": "https://godot2amiga.org/schemas/g2a/scene.schema.json",
        "id": scene_id,
        "source": main_scene_resource,
        "root": {
            "id": scene_id,
            "name": _scene_name_from_path(main_scene_resource),
            "type": "Node2D",
            "parent": null,
            "children": [],
        },
    }

    var diagnostics := {
        "$schema": "https://godot2amiga.org/schemas/g2a/diagnostics.schema.json",
        "errors": [],
        "warnings": [],
        "notes": [
            {
                "code": "G2A-M2-SKELETON",
                "message": "Scene traversal and asset export are not implemented yet.",
                "source": main_scene_resource,
            }
        ],
    }

    var writes := [
        ["manifest.json", manifest],
        ["project.json", project],
        ["export_profile.json", export_profile],
        [scene_output_path, scene_document],
        ["diagnostics/diagnostics.json", diagnostics],
    ]

    for write_spec: Array in writes:
        var write_error := _write_json_file(
            output_directory.path_join(str(write_spec[0])),
            write_spec[1]
        )
        if write_error != OK:
            return write_error

    return OK


func _write_json_file(path: String, value: Variant) -> Error:
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        var open_error := FileAccess.get_open_error()
        push_error(
            "Godot2Amiga: could not open '%s' for writing (error %d)."
            % [path, open_error]
        )
        return open_error

    file.store_string(JSON.stringify(value, "\t") + "\n")
    file.close()
    return OK


func _scene_id_from_path(scene_path: String) -> String:
    if scene_path.is_empty():
        return "main"
    return _slugify(scene_path.get_file().get_basename())


func _scene_name_from_path(scene_path: String) -> String:
    if scene_path.is_empty():
        return "Main"
    return scene_path.get_file().get_basename().capitalize()


func _slugify(value: String) -> String:
    var result := value.strip_edges().to_lower()
    result = result.replace(" ", "-")
    result = result.replace("_", "-")

    var allowed := ""
    for character: String in result:
        if character >= "a" and character <= "z":
            allowed += character
        elif character >= "0" and character <= "9":
            allowed += character
        elif character == "-":
            allowed += character

    while "--" in allowed:
        allowed = allowed.replace("--", "-")

    allowed = allowed.trim_prefix("-").trim_suffix("-")
    return allowed if not allowed.is_empty() else "unnamed-project"
