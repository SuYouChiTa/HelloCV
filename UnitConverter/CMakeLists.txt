# 1) 声明所需的最低 CMake 版本
cmake_minimum_required(VERSION 3.10)

# 2) 工程名、版本、语言
project(UnitConverter VERSION 1.0 LANGUAGES CXX)

# 3) C++ 标准（c++17标准，和当时cpp考试让用的一样）
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 4) 把 unitlib 子目录加进来
add_subdirectory(unitlib)

# 5) 生成可执行文件 unitconv
add_executable(unitconv
    src/main.cpp
)

# 6) 让 unitconv 链接 unitlib
# 链接 libunitlib.a 并 继承 unitlib 的 PUBLIC 头文件目录
target_link_libraries(unitconv
    PRIVATE
        unitlib
)

# 7) 打开常用警告
target_compile_options(unitconv
    PRIVATE
        -Wall
        -Wextra
)
