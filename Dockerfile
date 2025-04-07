FROM ubuntu AS base
RUN apt update && apt install -y nala
RUN nala fetch --auto 
RUN nala update

FROM base AS install_compressors
RUN nala install -y pigz

FROM ubuntu AS download_fabrics
WORKDIR /raw_hf
ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/conus/conus_nextgen.gpkg /raw_hf/conus_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/ak/ak_nextgen.gpkg /raw_hf/ak_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/gl/gl_nextgen.gpkg /raw_hf/gl_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/hi/hi_nextgen.gpkg /raw_hf/hi_nextgen.gpkg
# ADD https://lynker-spatial.s3-us-west-2.amazonaws.com/hydrofabric/v2.2/prvi/prvi_nextgen.gpkg /raw_hf/prvi_nextgen.gpkg


FROM base AS install_tools
# Install all the required tools
RUN nala install -y libsqlite3-mod-spatialite python3-pip
# install uv via pip as it doesn't work with the shell script
RUN pip3 install uv --break-system-packages
# it doesn't matter where this venv ends up, uv will globally cache this package
RUN uv venv && uv pip install ngiab_data_preprocess


FROM install_tools AS add_index
# This stage adds indices to the hydrofabric gpkg to allow much faster querying on some common fields
COPY --from=download_fabrics /raw_hf /raw_hf
RUN uv pip install ngiab_data_preprocess
RUN uv run python -c "from data_processing.gpkg_utils import verify_indices; verify_indices('/raw_hf/conus_nextgen.gpkg');"


FROM add_index AS fix_gages
# This is performed before hydrolocations are converted as it's easier to modify the tables
WORKDIR /workspace
COPY scripts/hydro/gages gages
RUN python3 gages/detect_flowpath_issues.py gages/gage_area.csv /raw_hf/conus_nextgen.gpkg
RUN python3 gages/update_gages.py 


FROM fix_gages AS hydrolocations_to_geom
# This stage converts the hydrolocations layer into the gpkg into a gpkg compliant geometry layer
COPY scripts/formatting/*hydrolocations_to_geom.* .
COPY scripts/formatting/utils.py .

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
WORKDIR /output/
COPY --from=hydrolocations_to_geom /raw_hf/conus_nextgen.gpkg .
RUN tar cf - "conus_nextgen.gpkg" | pigz > "conus_nextgen.tar.gz"

