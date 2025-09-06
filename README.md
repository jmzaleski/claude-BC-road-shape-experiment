idea here is to massage FSR road data from

https://www2.gov.bc.ca/gov/content/data/geographic-data-services/topographic-data/roads

such that it can be uploaded into caltopo and appear on a mobile map.

go to the page above, choose an area (all of BC is too big) and download a geojson file.
you want the "master demographic" variant (I don't know what this means)

rename or link the downloaded file to  "bc_roads.geojson" and run claude.py

If you make the area of interest AOI too big it will take too long to run
For instance, the first time I made it basically the whole southern part of the province and the .geojson was 1G.
python script ran okay, but merged .geojson was 37M which takes forever to load into caltopo.
Evidently caltopo does a lot of the work in javascript as chrome warns that the tab is using too much juice.

have to set up conda first
# Create environment
conda create -n fsr-merger python=3.11

# Activate it  
conda activate fsr-merger

# Install from your requirements.txt using conda-forge channel
conda install -c conda-forge --file requirements.txt

#then activate the appropriate python environment for the script by
conda activate fsr-merger

# Run the script. it reads from bc_roads.geojson and writes bc_fsrs_merged.geojson
python claude.py

