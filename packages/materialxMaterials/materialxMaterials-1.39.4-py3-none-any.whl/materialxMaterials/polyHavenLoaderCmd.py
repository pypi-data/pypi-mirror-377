'''
@file: polyhavenLoaderCmd.py
@brief: A command-line interface to fetch MaterialX assets from PolyHaven and download them.
'''
from pathlib import Path
import argparse
import json
import logging
import polyHavenLoader

logger = logging.getLogger('POLYH_CMD')
logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Fetch MaterialX assets from PolyHaven")
    parser.add_argument("-id", "--download_id", type=str, default="polystyrene", help="Filter ID to fetch MaterialX assets (e.g. 'polystyrene')")
    parser.add_argument("-res", "--download_resolution", type=str, default="1k", help="Resolution of the MaterialX assets to download (e.g. '1k', '2k', '4k', '8k') ")
    parser.add_argument("-fe", "--fetch", action='store_true', help="Fetch and save the MaterialX assets to a file")
    parser.add_argument("-l", "--load", action='store_true', help="Load the MaterialX assets")
    parser.add_argument("-df", "--data_folder", type=str, default="data/PolyHavenMaterialX", help="Data folder to save / load MaterialX assets")
    parser.add_argument("-c", "--count", type=int, default=None, help="Number of assets to fetch (default: 1)")

    args = parser.parse_args()
    data_file = "polyhaven_materialx_assets.json"
    fetch = args.fetch
    download_id = args.download_id
    resolution = args.download_resolution
    load = args.load
    data_folder = args.data_folder
    
    loader = polyHavenLoader.PolyHavenLoader()

    materialx_assets = None

    if fetch:
        fetch_count = args.count
        if fetch_count and fetch_count < 1:
            fetch_count = 1
        fetch_location = Path(data_folder) / data_file
        logger.info(f"Fetching MaterialX assets to {fetch_location}...")
        materialx_assets, all_assets, filtered_polyhaven_assets = loader.fetch_materialx_assets(download_id=download_id, max_items=fetch_count)
        with open(fetch_location, "w") as f:
            json.dump(materialx_assets, f, indent=4)

        # Write all_assets to JSON file:        
        all_location = Path(data_folder) / "polyhaven_assets.json"
        with open(all_location, "w") as f:
            json.dump(all_assets, f, indent=4)
            logger.info(f"Saved all assets to {all_location}")
        # Write filtered assets to JSON file:
        filtered_location = Path(data_folder) / "filtered_polyhaven_assets.json"
        with open(filtered_location, "w") as f:
            json.dump(filtered_polyhaven_assets, f, indent=4)
            logger.info(f"Saved MaterialX assets to {filtered_location}")

    elif load:
        load_location = Path(data_folder) / data_file
        with open(load_location, "r") as f:
            logger.info(f"Loaded MaterialX assets from {load_location}")
            materialx_assets = json.load(f)
        #json_string = json.dumps(materialx_assets, indent=4)
        #logger.info(f"MaterialX assets: {json_string}")

    if materialx_assets and download_id:
        # Find download entry by ID
        entry_id = download_id + '___' + resolution
        entry = materialx_assets.get(entry_id)
        if entry:
            logger.info(f"Downloading asset with ID '{download_id}', resolution '{resolution}'")
            asset_list = {entry_id: entry, resolution: resolution}
            id, mtlx_string, texture_binaries = loader.download_asset(asset_list)                
            loader.save_materialx_with_textures(id, mtlx_string, texture_binaries, data_folder)
        else:
            logger.info(f"No asset found with ID '{entry_id}' in the MaterialX assets.")
    else:
        logger.info("No operation specified.")

if __name__ == "__main__":
    main()