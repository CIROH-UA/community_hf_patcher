#!/bin/bash
docker build -t hf --target vpu_output . && \
docker run -d --name vpu_container hf sleep infinity && \
docker cp vpu_container:/workspace VPU && \
docker kill vpu_container && \
docker rm vpu_container #&& \
#aws configure set s3.max_concurrent_requests 200 && \
#aws s3 sync VPU s3://communityhydrofabric/hydrofabrics/community/VPU
