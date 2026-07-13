# M5.0.2c Clean Pack Contract

`pack.py` no longer scans the CMake build directory or guesses executable
names.

The contract is mandatory:

```json
{
  "project": {
    "id": "minimal",
    "name": "Minimal"
  },
  "build": {
    "cmake_target": "minimal",
    "artifact_name": "minimal"
  }
}
```

The compiled source artifact is resolved exactly as:

```text
COMPILE_INFO.build_directory / BUILD_INFO.build.artifact_name
```

If that file does not exist, packaging fails with `EXIT_INVALID_PROJECT`.

The generated-project output directory is not part of project identity. This
means a project with ID `minimal` can safely be generated into
`build/assets-demo`; packaging still reads `.g2a-build/minimal`.

Generated CMake keeps `${PROJECT_NAME}` as the executable target reference,
with `project(<cmake_target> C)` defining its value.
