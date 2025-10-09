#!/bin/bash
docker build -t hf --build-context local_copy=<path_to_local_copy> .  && \
docker run -d --name hf_container hf sleep infinity && \
docker cp hf_container:/output/conus_nextgen.gpkg . && \
docker cp hf_container:/output/conus_nextgen.tar.gz . && \
docker cp hf_container:/output/ak_nextgen.gpkg . && \
docker cp hf_container:/output/ak_nextgen.tar.gz . && \
# docker cp hf_container:/output/gl_nextgen.gpkg . && \
# docker cp hf_container:/output/gl_nextgen.tar.gz . && \
docker cp hf_container:/output/hi_nextgen.gpkg . && \
docker cp hf_container:/output/hi_nextgen.tar.gz . && \
docker cp hf_container:/output/prvi_nextgen.gpkg . && \
docker cp hf_container:/output/prvi_nextgen.tar.gz . && \
docker cp hf_container:/output/gage_replacements.csv . && \
docker kill hf_container && \
docker rm hf_container # && \
#aws s3 cp ./gage_replacements.csv s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./conus_nextgen.gpkg s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./conus_nextgen.tar.gz s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./ak_nextgen.gpkg s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./ak_nextgen.tar.gz s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./hi_nextgen.gpkg s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./hi_nextgen.tar.gz s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./gl_nextgen.gpkg s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./gl_nextgen.tar.gz s3://communityhydrofabric/hydrofabrics/community/
#aws s3 cp ./prvi_nextgen.gpkg s3://communityhydrofabric/hydrofabrics/community/ && \
#aws s3 cp ./prvi_nextgen.tar.gz s3://communityhydrofabric/hydrofabrics/community/ && \
