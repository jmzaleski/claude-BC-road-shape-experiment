idea here is to massage FSR road data from

https://www2.gov.bc.ca/gov/content/data/geographic-data-services/topographic-data/roads

such that it can be uploaded into caltopo and appear on a mobile map.

go to the page above, choose an area (all of BC is too big) and download a geojson file.
rename the downloaded file to  "bc_roads.geojson" and run claude.py


have to set up conda first
# Create environment
conda create -n fsr-merger python=3.11

# Activate it  
conda activate fsr-merger

# Install from your requirements.txt using conda-forge channel
conda install -c conda-forge --file requirements.txt

#then activate the appropriate python environment for the script by
conda activate fsr-merger

# Run your script as many times as you want
python claude.py
