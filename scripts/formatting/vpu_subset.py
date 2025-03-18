from data_processing.file_paths import file_paths
from data_processing.subset import subset_vpu
from pathlib import Path
import os
def main():
    source_conus_gpkg = Path('/raw_hf/conus_nextgen.gpkg')
    dest_path = file_paths.conus_hydrofabric
    no_update_file = file_paths.no_update_hf

    
    # Create the no update file so the preprocessor doesn't try to download the old hydrofabric
    if not no_update_file.parent.exists():
        os.makedirs(no_update_file.parent)
    no_update_file.touch()

    # symlink the new hf to the location the preprocessor expects it to be
    dest_path.symlink_to(source_conus_gpkg)

    # List of VPUs
    vpus=["01","02","03","03N","03S","03W","04","05","06","07","08","09","10","10L","10U","11","12","13","14","15","16","17","18"]
    # 03 is 03N + 03S + 03W,  10 is 10L + 10U

    for vpu in vpus:
        subset_vpu(vpu, output_gpkg_path=Path(f'./vpu-{vpu}_subset.gpkg'))
    

if __name__ == "__main__":
    main()