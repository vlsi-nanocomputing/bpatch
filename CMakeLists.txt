cmake_minimum_required(VERSION 3.5.0)
project(patch VERSION 0.1.0 LANGUAGES C)

add_executable(bpatch main.c bpatch.c header_sbsfu.c)

