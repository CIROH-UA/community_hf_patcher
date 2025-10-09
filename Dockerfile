FROM ubuntu AS base
RUN apt update && apt install -y nala

FROM base AS install_compressors
RUN nala install -y pigz

FROM ubuntu AS download_fabrics
WORKDIR /raw_hf
COPY --from=local_copy conus_nextgen.gpkg /raw_hf/conus_nextgen.gpkg
COPY --from=local_copy ak_nextgen.gpkg /raw_hf/ak_nextgen.gpkg
# COPY --from=local_copy gl_nextgen.gpkg /raw_hf/gl_nextgen.gpkg
COPY --from=local_copy hi_nextgen.gpkg /raw_hf/hi_nextgen.gpkg
COPY --from=local_copy prvi_nextgen.gpkg /raw_hf/prvi_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/conus/conus_nextgen.gpkg /raw_hf/conus_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/ak/ak_nextgen.gpkg /raw_hf/ak_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/gl/gl_nextgen.gpkg /raw_hf/gl_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/hi/hi_nextgen.gpkg /raw_hf/hi_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/prvi/prvi_nextgen.gpkg /raw_hf/prvi_nextgen.gpkg

FROM base AS install_tools
WORKDIR /workspace
# Install all the required tools
RUN nala install -y libsqlite3-mod-spatialite python3-pip sqlite3
# install uv via pip as it doesn't work with the shell script
RUN pip3 install uv --break-system-packages
# it doesn't matter where this venv ends up, uv will globally cache this package
COPY scripts/formatting/utils.py .
COPY --from=dev . ngiab_data_preprocess
RUN uv venv && uv pip install ./ngiab_data_preprocess && uv pip install proj

FROM install_tools AS remove_error_table
COPY --from=download_fabrics /raw_hf /raw_hf
COPY scripts/formatting/remove_error_table.* .
RUN uv run remove_error_table.py

FROM remove_error_table AS make_uniform
COPY scripts/formatting/rename_cols.py .
RUN uv run rename_cols.py

FROM make_uniform AS add_index
# This stage adds indices to the hydrofabric gpkg to allow much faster querying on some common fields
RUN uv pip install ngiab_data_preprocess
RUN uv run python -c "from data_processing.gpkg_utils import verify_indices; verify_indices('/raw_hf/conus_nextgen.gpkg');"
RUN uv run python -c "from data_processing.gpkg_utils import verify_indices; verify_indices('/raw_hf/ak_nextgen.gpkg');"
# RUN uv run python -c "from data_processing.gpkg_utils import verify_indices; verify_indices('/raw_hf/gl_nextgen.gpkg');"
RUN uv run python -c "from data_processing.gpkg_utils import verify_indices; verify_indices('/raw_hf/hi_nextgen.gpkg');"
RUN uv run python -c "from data_processing.gpkg_utils import verify_indices; verify_indices('/raw_hf/prvi_nextgen.gpkg');"

FROM add_index AS assign_srs
RUN sqlite3 /raw_hf/prvi_nextgen.gpkg "UPDATE 'gpkg_geometry_columns' SET srs_id = '6566';"


FROM add_index AS fix_gages
# This is performed before hydrolocations are converted as it's easier to modify the tables
COPY scripts/hydro/gages gages
RUN python3 gages/detect_flowpath_issues.py gages/gage_area.csv /raw_hf/conus_nextgen.gpkg
RUN python3 gages/update_gages.py
RUN sqlite3 /raw_hf/ak_nextgen.gpkg "UPDATE 'flowpath-attributes' SET gage = '15236900', gage_nex_id = 'nex-8435' WHERE id = 'wb-8434';"


FROM add_index AS hydrolocations_to_geom
# This stage converts the hydrolocations layer into the gpkg into a gpkg compliant geometry layer
COPY scripts/formatting/*hydrolocations_to_geom.* .
RUN uv venv && uv pip install pyproj
RUN uv run hydrolocations_to_geom.py


#####################################
#           OUTPUT BELOW            #
#####################################

FROM install_tools AS subset_vpus
WORKDIR /workspace
RUN uv pip install ngiab_data_preprocess
COPY --from=hydrolocations_to_geom /raw_hf/conus_nextgen.gpkg /raw_hf/conus_nextgen.gpkg
# add VPU subsetting using the preprocssor
COPY scripts/formatting/vpu_subset.py .
RUN uv run vpu_subset.py

FROM install_compressors AS vpu_output
WORKDIR /workspace
COPY --from=subset_vpus /workspace/*.gpkg .
COPY scripts/formatting/compress_vpus.sh .
RUN ./compress_vpus.sh

FROM install_compressors AS output
# Compress the output
WORKDIR /output

COPY --from=fix_gages /raw_hf/ak_nextgen.gpkg .
# COPY --from=add_index /raw_hf/gl_nextgen.gpkg .
COPY --from=add_index /raw_hf/hi_nextgen.gpkg .
COPY --from=assign_srs /raw_hf/prvi_nextgen.gpkg .
RUN tar cf - "ak_nextgen.gpkg" | pigz > "ak_nextgen.tar.gz"
# RUN tar cf - "gl_nextgen.gpkg" | pigz > "gl_nextgen.tar.gz"
RUN tar cf - "hi_nextgen.gpkg" | pigz > "hi_nextgen.tar.gz"
RUN tar cf - "prvi_nextgen.gpkg" | pigz > "prvi_nextgen.tar.gz"

COPY --from=fix_gages /workspace/gage_replacements.csv .
COPY --from=hydrolocations_to_geom /raw_hf/conus_nextgen.gpkg .
RUN tar cf - "conus_nextgen.gpkg" | pigz > "conus_nextgen.tar.gz"
