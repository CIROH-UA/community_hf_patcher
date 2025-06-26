# Community Hydrofabric Patcher

This repository serves as the basis of the **CIROH Community Hydrofabric**, a temporary fork of [Lynker Spatial](lynker-spatial.com)'s **[NextGen Hydrofabric v2.2](https://www.lynker-spatial.com/data?path=hydrofabric%2Fv2.2%2Fconus%2F)**. This fork contains adjustments that improve the hydrofabric's compatibility with CIROH projects, including the [NextGen In A Box](https://ngiab.ciroh.org) ecosystem. These changes are slated for inclusion in the NextGen Hydrofabric v3, which will supplant this fork when it is released.

If you'd like to submit changes for long-term inclusion in the NextGen Hydrofabric, then you're most likely looking for Lynker Spatial's [**community.fabric**](https://github.com/lynker-spatial/community.fabric) repository.

This repository consists of scripts and Docker configurations that apply this fork's patches. Upon running, the patched hydrofabric is published to the [**Community Hydrofabric bucket**](https://communityhydrofabric.s3.us-east-1.amazonaws.com/index.html#hydrofabrics/community/) on AWS S3.

The [source hydrofabric](https://www.lynker-spatial.com/data?path=hydrofabric%2Fv2.2%2Fconus%2F) is provided by Lynker Spatial [under the ODbL license](https://lynker-spatial.s3-us-west-2.amazonaws.com/copyright.html).

## Current Patches
* Corrects the gage to flowpath mapping of around 4500 gages.
   * A full list [is available here](https://communityhydrofabric.s3.us-east-1.amazonaws.com/hydrofabrics/community/gage_replacements.csv) in the [Community Hydrofabric bucket](https://communityhydrofabric.s3.us-east-1.amazonaws.com/index.html#hydrofabrics/community/).
   * Detailed information regarding this patch is available in its [pull request](https://github.com/CIROH-UA/community_hf_patcher/pull/1).
* Reformats hydrolocation table to be gpkg compliant.
   * This allows the hydrofabric to appear as geometry in GIS applications and tools.
* Adds database indices to commonly searched values to speed up retrieval.
   * Example: `select * from divides where id="wb-1234"`

## Usage

### Prerequisites

- Docker
- AWS CLI (if you plan to upload files to S3)

### Running

The full build process is handled by the below shell script:
```bash
./generate_hydrofabric.sh
```
If you'd like to upload files to an AWS S3 bucket, then uncomment the AWS commands in the shell scripts.

## Repository Structure

- **`generate_hydrofabric.sh`**: The main entrypoint of the patcher. Responsible for building and running the Docker container, extracting processed hydrofabric files, and optionally uploading them to an S3 bucket.
- **`generate_vpus.sh`**: A secondary entrypoint for the patcher. It functions similarly to `generate_hydrofabric.sh`, but instead subsets the hydrofabric into individual VPUs.
- **`Dockerfile`**: A multi-stage Dockerfile that defines the steps for downloading, processing, and compressing hydrofabric data.
- **`scripts/`**: Contains Python and shell scripts for specific data processing tasks, such as updating gages, converting hydrolocations, and subsetting VPUs.
- **`scripts/formatting`**: Scripts purely related to how the information is stored in the hydrofabric.
- **`scripts/hydro`**: Scripts that modify the hydrologic data. Any changes that would alter the output of a simulation will be here.

## Workflow Overview
Docker is being used in a *slightly* unconventional way here to take advantage of the automatic hashing of files and caching of steps to only re-run sections that have been modified. The ADD command on the source hydrofabric is extremely slow, so this process will need to be reworked if the fork is updated frequently.


1. **Build and Run the Docker Container**:
   Each of the shell scripts call on the Dockerfile to build and run the container. The Dockerfile defines multiple stages for downloading, processing, and compressing hydrofabric data. Each stage performs a specific task, such as:
   - Downloading raw hydrofabric files.
   - Adding indices for faster querying.
   - Updating gages and converting hydrolocations.
   - Subsetting VPUs and compressing the output.

2. **Extract files**:
    Once all stages are complete, the script extracts the processed files from the container.

    `generate_hydrofabric.sh` will export the following:
	- `conus_nextgen.gpkg`: The complete patched hydrofabric.
	- `conus_nextgen.tar.gz`: Identical to the above, but compressed as a tarball.
	- `gage_replacements.csv`: A catalog of which gages were altered by the patcher.

    `generate_vpus.sh` will export the following:
	- `VPU`: A folder containing separate hydrofabrics for each VPU.
	- `VPU/compressed`: A folder containing compressed tarballs of the VPU hydrofabrics.

3. **Upload to S3 (Optional)**:
   If you have valid credentials to the Community Hydrofabric S3 bucket, uncomment the lines in `generate_hydrofabric.sh` and `generate_vpus.sh` to upload the output automatically.
