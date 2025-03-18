#!/bin/bash

# REQUIREMENTS TO RUN THIS
# pigz, a parallel compression cli tool. or just modify line 51 and 57 to tar -cxvf
# uvx, cli tool for managing and running python packages https://docs.astral.sh/uv/getting-started/installation/

# List of VPUs
vpus=("01" "02" "03" "03N" "03S" "03W" "04" "05" "06" "07" "08" "09" "10" "10L" "10U" "11" "12" "13" "14" "15" "16" "17" "18")
# 03 is 03N + 03S + 03W,  10 is 10L + 10U

# Helper functions to speed up compression, useful to add to ~/.bashrc too!
punzip() {
    if [ $# -eq 0 ]; then
        echo "Usage: punzip <filename.tar.gz>"
        return 1
    fi
    pigz -dc "$1" | tar xvf -
}

pzip() {
    if [ $# -lt 2 ]; then
        echo "Usage: pzip <output_filename.tar.gz> <input_file_or_directory> [additional_files_or_directories...]"
        return 1
    fi
    output_file="$1"
    shift
    tar cf - "$@" | pigz > "$output_file"
}


# Create a directory for compressed files
mkdir -p ./compressed

# Create a tar of each VPU
for gpkg_file in ./vpu-*.gpkg; do
    # Extract the base name without extension
    base_name=$(basename "$gpkg_file" .gpkg)
    # pzip is parallel compression equivalent to tar -czvf
    pzip "./compressed/${base_name}.tar.gz" "$gpkg_file"
done

# Create a single tarball containing all VPU .gpkg files
# Expand the wildcard into a list of files
gpkg_files=(./vpu-*.gpkg)
pzip ./compressed/all_vpus.tar.gz "${gpkg_files[@]}"

echo "All VPU tarballs have been created and compressed."