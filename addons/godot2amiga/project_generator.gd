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
            ProjectSettings.globalize_path(
                output_directory.path_join(directory_name)
            )
        )
        if child_error != OK:
            push_error(
                "Godot2Amiga: could not create '%s' (error %d)."
                % [directory_name, child_error]
            )
            return child_error

    var project_name := str(
        ProjectSettings.get_setting(
            "application/config/name",
            "Unnamed project"
        )
    )
    var main_scene_resource := str(
        ProjectSettings.get_setting(
            "application/run/main_scene",
            ""
        )
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
        "$schema": (
            "https://godot2amiga.org/"
            + "schemas/g2a/manifest.schema.json"
        ),
        "format": "g2a",
        "format_version": FORMAT_VERSION,
        "generator": {
            "name": "Godot2Amiga",
            "version": GENERATOR_VERSION,
            "godot_version": godot_version,
        },
    }

    var project := {
        "$schema": (
            "https://godot2amiga.org/"
            + "schemas/g2a/project.schema.json"
        ),
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
        "$schema": (
            "https://godot2amiga.org/"
            + "schemas/g2a/export-profile.schema.json"
        ),
        "id": "amiga500-ocs-pal",
        "machine": "Amiga 500",
        "chipset": "OCS",
        "cpu": "68000",
        "video_standard": "PAL",
        "chip_ram_kib": 512,
        "fast_ram_kib": 0,
        "runtime": "ACE",
    }

    var scene_result := _generate_scene_document(
        main_scene_resource,
        scene_id
    )
    if scene_result["error"] != OK:
        return int(scene_result["error"])

    var scene_document: Dictionary = scene_result["document"]

    var diagnostics := {
        "$schema": (
            "https://godot2amiga.org/"
            + "schemas/g2a/diagnostics.schema.json"
        ),
        "errors": [],
        "warnings": scene_result["warnings"],
        "notes": [
            {
                "code": "G2A-M72A-SCENE-TRAVERSAL",
                "message": (
                    "Scene traversal is implemented. "
                    + "Texture and asset export are not implemented yet."
                ),
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


func _generate_scene_document(
    scene_path: String,
    scene_id: String
) -> Dictionary:
    if scene_path.is_empty():
        push_error(
            "Godot2Amiga: application/run/main_scene is not configured."
        )
        return {
            "error": ERR_FILE_NOT_FOUND,
            "document": {},
            "warnings": [],
        }

    var packed_scene := load(scene_path) as PackedScene
    if packed_scene == null:
        push_error(
            "Godot2Amiga: could not load main scene '%s'."
            % scene_path
        )
        return {
            "error": ERR_FILE_CANT_OPEN,
            "document": {},
            "warnings": [],
        }

    var root_node := packed_scene.instantiate()
    if root_node == null:
        push_error(
            "Godot2Amiga: could not instantiate main scene '%s'."
            % scene_path
        )
        return {
            "error": ERR_CANT_CREATE,
            "document": {},
            "warnings": [],
        }

    var used_ids: Dictionary = {}
    var warnings: Array = []
    var root_document := _export_node(
        root_node,
        null,
        used_ids,
        warnings
    )

    root_node.free()

    return {
        "error": OK,
        "document": {
            "$schema": (
                "https://godot2amiga.org/"
                + "schemas/g2a/scene.schema.json"
            ),
            "id": scene_id,
            "source": scene_path,
            "root": root_document,
        },
        "warnings": warnings,
    }


func _export_node(
    node: Node,
    parent_id: Variant,
    used_ids: Dictionary,
    warnings: Array
) -> Dictionary:
    var node_id := _unique_node_id(
        _slugify(str(node.name)),
        used_ids
    )

    var properties := _export_node_properties(node, warnings)

    var children: Array = []
    for child: Node in node.get_children():
        children.append(
            _export_node(
                child,
                node_id,
                used_ids,
                warnings
            )
        )

    var document := {
        "id": node_id,
        "name": str(node.name),
        "type": node.get_class(),
        "parent": parent_id,
        "children": children,
    }

    if not properties.is_empty():
        document["properties"] = properties

    return document


func _export_node_properties(
    node: Node,
    warnings: Array
) -> Dictionary:
    var properties := {}

    if node is Node2D:
        var node_2d := node as Node2D
        properties["position"] = {
            "x": int(round(node_2d.position.x)),
            "y": int(round(node_2d.position.y)),
        }

        if (
            not is_equal_approx(
                node_2d.position.x,
                float(properties["position"]["x"])
            )
            or not is_equal_approx(
                node_2d.position.y,
                float(properties["position"]["y"])
            )
        ):
            warnings.append(
                {
                    "code": "G2A-M72A-ROUNDED-POSITION",
                    "message": (
                        "Node2D position was rounded to integer coordinates."
                    ),
                    "source": str(node.get_path()),
                }
            )

    if node is CanvasItem:
        var canvas_item := node as CanvasItem
        properties["visible"] = canvas_item.visible
        properties["z_index"] = canvas_item.z_index

    if node is Sprite2D:
        var sprite := node as Sprite2D
        if sprite.texture != null:
            properties["texture"] = _resource_id(
                sprite.texture,
                str(node.name)
            )
            warnings.append(
                {
                    "code": "G2A-M72A-TEXTURE-REFERENCE-ONLY",
                    "message": (
                        "Sprite2D texture reference exported, "
                        + "but asset conversion is not implemented yet."
                    ),
                    "source": str(node.get_path()),
                }
            )

    return properties


func _resource_id(
    resource: Resource,
    fallback_name: String
) -> String:
    if not resource.resource_path.is_empty():
        return _slugify(
            resource.resource_path.get_file().get_basename()
        )

    if not resource.resource_name.is_empty():
        return _slugify(resource.resource_name)

    return _slugify(fallback_name)


func _unique_node_id(
    base_id: String,
    used_ids: Dictionary
) -> String:
    var candidate := base_id
    var suffix := 2

    while used_ids.has(candidate):
        candidate = "%s-%d" % [base_id, suffix]
        suffix += 1

    used_ids[candidate] = true
    return candidate


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
    return allowed if not allowed.is_empty() else "unnamed-node"
