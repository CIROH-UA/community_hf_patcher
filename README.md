# Community Hydrofabric Patcher

This repository contains scripts and Docker configurations for processing and patching hydrofabric data.

The [source hydrofabric](https://www.lynker-spatial.com/data?path=hydrofabric%2Fv2.2%2Fconus%2F) is provided by [lynker-spatial under the ODbL license.](https://lynker-spatial.s3-us-west-2.amazonaws.com/copyright.html)

The output of this repository is available in the [community hydrofabric bucket](https://communityhydrofabric.s3.us-east-1.amazonaws.com/index.html#hydrofabrics/community/)

# [Click here for the current list of community patches](#current-patches)

## Usage

### Prerequisites

- Docker installed on your system.
- AWS CLI configured if you plan to upload files to S3.

### Steps

1. Build the Docker image:
   ```bash
   ./generate_hydrofabric.sh
    ```

## Repository Structure

- **`generate_hydrofabric.sh`**: A Bash script to build and run the Docker container, extract processed hydrofabric files, and optionally upload them to an S3 bucket.
- **`generate_vpus.sh`**: Generate the hydrofabric, then split it up by VPU and optionally upload them to an S3 bucket
- **`Dockerfile`**: A multi-stage Dockerfile that defines the steps for downloading, processing, and compressing hydrofabric data.
- **`scripts/`**: Contains Python and shell scripts for specific data processing tasks, such as updating gages, converting hydrolocations, and subsetting VPUs.
- **`scripts/formatting`**: Scripts purely related to how the information is stored in the hydrofabric
- **`scripts/hydro`**: Scripts that modify the hydrologic data. Any changes that would alter the output of a simulation will be here.

## Workflow Overview
Docker is being used in a *slightly* unconventional way here to take advantage of the automatic hashing of files and caching of steps to only re-run sections that have been modified. The ADD command on the source hydrofabric is extremely slow so this process will need to be reworked if it is updated frequently.


1. **Build the Docker Image**:
   The Dockerfile defines multiple stages for downloading, processing, and compressing hydrofabric data. Each stage performs a specific task, such as:
   - Downloading raw hydrofabric files.
   - Updating gages and converting hydrolocations.
   - Adding indices for faster querying.
   - Subsetting VPUs and compressing the output.

2. **Run the Docker Container**:
   Use the `generate_hydrofabric.sh` script to build and run the container. The script extracts the processed files (`conus_nextgen.gpkg` and `conus_nextgen.tar.gz`) from the container.

3. **Upload to S3 (Optional)**:
   If you have valid credentials to the community hydrofabric s3 bucket, uncomment the lines in `generate_hydrofabric.sh` to upload the output automatically.

# Current Patches
* Correct gage-10154200 position to wb-2863631
* Reformat hydrolocation table to be gpkg compliant (should now show up in GIS application / tools as geometry)
* Add database indices to commonly searched values to speed up operations. e.g. select * from divides where id="wb-1234"