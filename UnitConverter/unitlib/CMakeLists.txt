# ===== unitlib：把 unitlib.cpp 编译成静态库 =====
#
# 这个文件只负责"库"这一件事：
#   1) 把 src/unitlib.cpp 编成静态库 libunitlib.a
#   2) 把 include/ 目录标记为 PUBLIC，让链接本库的目标自动获得头文件搜索路径

add_library(unitlib STATIC
    src/unitlib.cpp
)

# PUBLIC 的含义：
#   既用于编译 unitlib 自己，也"传递"给任何 target_link_libraries 了 unitlib 的目标。
#   如果写成 PRIVATE，main.cpp 里 #include "unitlib.h" 就会报
#   fatal error: unitlib.h: No such file or directory
target_include_directories(unitlib
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)
