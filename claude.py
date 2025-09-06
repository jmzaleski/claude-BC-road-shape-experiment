#!/usr/bin/env python3
"""
BC FSR Road Segment Merger
Loads BC road data and merges Forest Service Road segments
"""

import geopandas as gpd
import pandas as pd
import re
from shapely.ops import linemerge
from pathlib import Path
import sys

def is_fsr(road_name):
    """Check if road name matches FSR patterns"""
    if pd.isna(road_name):
        return False
    
    road_name = str(road_name).upper()
    
    # Common FSR patterns in BC
    fsr_patterns = [
        r'.*FSR.*',                    # Contains "FSR"
        r'.*FOREST.*SERVICE.*ROAD.*',  # "Forest Service Road"
        r'.*FORESTRY.*ROAD.*',         # "Forestry Road"
        r'^[A-Z]+\s*\d+\s*FSR$',      # "SMITH 100 FSR"
        r'^\d+\s*FSR$',               # "1200 FSR"
        r'.*BRANCH.*FSR.*',           # "West Branch FSR"
        r'.*CREEK.*FSR.*',            # "Bear Creek FSR"
        r'.*MAIN.*FSR.*',             # "Slocan Main FSR"
    ]
    
    return any(re.match(pattern, road_name) for pattern in fsr_patterns)

def explore_road_names(gdf, output_file="fsr_names.txt"):
    """Explore and save potential FSR names"""
    print("Exploring road names...")
    
    # Get all unique road names
    unique_names = gdf['road_name'].dropna().unique()
    print(f"Total unique road names: {len(unique_names)}")
    
    # Find potential FSRs
    potential_fsrs = [name for name in unique_names 
                      if any(keyword in str(name).upper() 
                            for keyword in ['FSR', 'FOREST', 'FORESTRY'])]
    
    print(f"Found {len(potential_fsrs)} potential FSR names")
    
    # Save to file for inspection
    with open(output_file, 'w') as f:
        f.write("Potential FSR Names Found:\n")
        f.write("=" * 40 + "\n")
        for name in sorted(potential_fsrs):
            f.write(f"{name}\n")
    
    print(f"FSR names saved to {output_file}")
    
    # Show first 20 in console
    print("\nFirst 20 potential FSR names:")
    for name in sorted(potential_fsrs)[:20]:
        print(f"  {name}")
    
    return potential_fsrs

def merge_fsr_segments(gdf):
    """Filter for FSRs and merge segments"""
    print("\nFiltering for FSR roads...")
    
    # Apply FSR filter
    fsr_roads = gdf[gdf['road_name'].apply(is_fsr)].copy()
    print(f"Found {len(fsr_roads)} FSR segments out of {len(gdf)} total segments")
    
    if len(fsr_roads) == 0:
        print("No FSR roads found with current patterns!")
        return None
    
    print("\nMerging FSR segments by road name...")
    merged_fsrs = []
    
    for road_name, group in fsr_roads.groupby('road_name'):
        # Merge contiguous segments of the same FSR
        try:
            merged_geom = linemerge(group.geometry.tolist())
            
            merged_fsrs.append({
                'road_name': road_name,
                'original_segments': len(group),
                'total_length_m': group.geometry.length.sum(),
                'geometry': merged_geom
            })
            
        except Exception as e:
            print(f"Error merging {road_name}: {e}")
            continue
    
    if not merged_fsrs:
        print("No FSR segments could be merged!")
        return None
    
    fsr_gdf = gpd.GeoDataFrame(merged_fsrs, crs=fsr_roads.crs)
    
    print(f"Merged into {len(fsr_gdf)} unique FSR roads")
    print(f"Average segments per FSR: {sum(f['original_segments'] for f in merged_fsrs) / len(merged_fsrs):.1f}")
    
    return fsr_gdf

def main():
    """Main execution function"""
    # Check for input file
    geojson_file = "bc_roads.geojson"
    geojson_file = "DRA_DGTL_ROAD_ATLAS_MPAR_SP.geojson"
    
    if not Path(geojson_file).exists():
        print(f"Error: {geojson_file} not found!")
        print("Please download BC road data and save as 'bc_roads.geojson'")
        print("You can download from BC Data Catalogue:")
        print("https://catalogue.data.gov.bc.ca/dataset/digital-road-atlas-dra-demographic-partially-attributed-roads")
        return
    
    try:
        print(f"Loading {geojson_file}...")
        gdf = gpd.read_file(geojson_file)
        print(f"Loaded {len(gdf)} road segments")
        
        # Show column information
        print(f"\nDataset columns: {list(gdf.columns)}")
        print(f"CRS: {gdf.crs}")
        
        # Explore road names
        potential_fsrs = explore_road_names(gdf)
        
        if not potential_fsrs:
            print("No potential FSR roads found. Check the road name patterns.")
            return
        
        # Merge FSR segments
        merged_fsrs = merge_fsr_segments(gdf)
        
        if merged_fsrs is not None:
            # Save results
            output_file = "bc_fsrs_merged.geojson"
            merged_fsrs.to_file(output_file, driver='GeoJSON')
            print(f"\nMerged FSR roads saved to {output_file}")
            
            # Show summary statistics
            print("\nSummary Statistics:")
            print(f"Total FSR roads: {len(merged_fsrs)}")
            print(f"Total original segments: {merged_fsrs['original_segments'].sum()}")
            print(f"Average reduction: {((merged_fsrs['original_segments'].sum() - len(merged_fsrs)) / merged_fsrs['original_segments'].sum() * 100):.1f}%")
            
            # Show top 10 FSRs by segment count
            top_fsrs = merged_fsrs.nlargest(10, 'original_segments')
            print(f"\nTop 10 FSRs by original segment count:")
            for _, row in top_fsrs.iterrows():
                print(f"  {row['road_name']}: {row['original_segments']} segments")
    
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
