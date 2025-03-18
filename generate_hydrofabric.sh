#!/bin/bash
docker build -t hf --target output .
docker run -d --name hf hf sleep infinity
docker cp hf:/output/conus_nextgen.gpkg .
docker cp hf:/output/conus_nextgen.tar.gz .
docker kill hf
aws s3 cp ./conus_nextgen.gpkg s3://communityhydrofabric/hydrofabrics/community
aws s3 cp ./conus_nextgen.tar.gz s3://communityhydrofabric/hydrofabrics/community