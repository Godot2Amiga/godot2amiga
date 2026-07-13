# M5.0.2b

This patch replaces the previous M5.0.2 proposal.

Changes:
- Preserve `${PROJECT_NAME}` throughout generated CMake.
- BUILD_INFO.json is mandatory.
- pack.py reads only build.artifact_name/build.cmake_target.
- Remove legacy artifact guessing.
- Update tests to generate BUILD_INFO.json.
- Update ACE integration test to expect `${PROJECT_NAME}`.

Target outcome: 116/116 tests passing.
