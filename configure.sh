cd c
cmake -B ../build
cd ../build
make
echo path_patch_exec = r\"$PWD/bpatch\" > ../path_bpatch.py
