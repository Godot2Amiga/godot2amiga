@tool
extends EditorPlugin

const MENU_EXPORT := "Godot2Amiga/Export ACE C skeleton"
const DEFAULT_OUTPUT_DIRECTORY := "res://build/amiga"

var _generator: RefCounted


func _enter_tree() -> void:
    _generator = preload("res://addons/godot2amiga/project_generator.gd").new()
    add_tool_menu_item(MENU_EXPORT, _export_project)


func _exit_tree() -> void:
    remove_tool_menu_item(MENU_EXPORT)
    _generator = null


func _export_project() -> void:
    if _generator == null:
        push_error("Godot2Amiga generator is not initialized.")
        return

    var error: Error = _generator.generate(DEFAULT_OUTPUT_DIRECTORY)
    if error != OK:
        push_error(
            "Godot2Amiga export failed with error %d. See the editor output for details."
            % error
        )
        return

    print(
        "Godot2Amiga: generated ACE C skeleton in %s"
        % ProjectSettings.globalize_path(DEFAULT_OUTPUT_DIRECTORY)
    )
    EditorInterface.get_resource_filesystem().scan()
