cmake_minimum_required(VERSION 3.20)

project(minimal C)

add_executable(${PROJECT_NAME}
    src/main.c
    src/generated_project.c
)

target_include_directories(${PROJECT_NAME} PRIVATE include)
