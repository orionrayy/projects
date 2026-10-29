cmake_minimum_required(VERSION 3.22)
project(dqbridge LANGUAGES CXX)

add_library(dqbridge SHARED
    src/bridge_core.cpp
    src/native_cheat_router_v84.cpp
    src/jni_bridge.cpp
)
target_include_directories(dqbridge PRIVATE include)
target_compile_features(dqbridge PRIVATE cxx_std_17)
target_compile_options(dqbridge PRIVATE -Wall -Wextra -Werror)
target_link_libraries(dqbridge PRIVATE dl)

# Source prototype only. This project does not package an APK or inject itself
# into Dungeon Quest; build only in an authorized, isolated development target.
