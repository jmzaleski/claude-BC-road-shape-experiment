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

def filter_fsr_segments(gdf):
    """Fast filter for FSR segments using vectorized operations"""
    print("Filtering for FSR segments...")
    
    # First filter: ROAD_CLASS must be "resource" 
    resource_mask = gdf['ROAD_CLASS'] == 'resource'
    print(f"Found {resource_mask.sum()} segments with ROAD_CLASS='resource'")
    
    # Second filter: ROAD_NAME_FULL must contain "FSR"
    # Use vectorized string operations for speed
    fsr_mask = gdf['ROAD_NAME_FULL'].str.contains('FSR', case=False, na=False)
    
    # Combine both conditions
    fsr_segments = gdf[resource_mask & fsr_mask].copy()
    
    print(f"Found {len(fsr_segments)} FSR segments out of {len(gdf)} total segments")
    print(f"Unique FSRs: {fsr_segments['ROAD_NAME_FULL'].nunique()}")
    
    return fsr_segments

def explore_fsr_data(fsr_gdf, output_file="fsr_analysis.txt"):
    """Analyze FSR data and save results"""
    print("Analyzing FSR data...")
    
    # Get FSR statistics
    fsr_names = fsr_gdf['ROAD_NAME_FULL'].unique()
    segment_counts = fsr_gdf.groupby('ROAD_NAME_FULL').size()
    
    print(f"Found {len(fsr_names)} unique FSRs")
    print(f"Total FSR segments: {len(fsr_gdf)}")
    print(f"Average segments per FSR: {len(fsr_gdf) / len(fsr_names):.1f}")
    
    # Save detailed analysis
    with open(output_file, 'w') as f:
        f.write("BC FSR Analysis\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total FSR segments: {len(fsr_gdf)}\n")
        f.write(f"Unique FSRs: {len(fsr_names)}\n")
        f.write(f"Average segments per FSR: {len(fsr_gdf) / len(fsr_names):.1f}\n\n")
        
        f.write("FSRs with most segments:\n")
        f.write("-" * 30 + "\n")
        top_fsrs = segment_counts.nlargest(20)
        for fsr_name, count in top_fsrs.items():
            f.write(f"{fsr_name}: {count} segments\n")
        
        f.write("\n\nAll FSR Names:\n")
        f.write("-" * 20 + "\n")
        for name in sorted(fsr_names):
            f.write(f"{name}\n")
    
    print(f"Analysis saved to {output_file}")
    
    # Show top FSRs in console
    print("\nTop 10 FSRs by segment count:")
    top_10 = segment_counts.nlargest(10)
    for fsr_name, count in top_10.items():
        print(f"  {fsr_name}: {count} segments")
    
    return segment_counts

def merge_fsr_segments(fsr_gdf):
    """Efficiently merge FSR segments by road name"""
    print("\nMerging FSR segments by ROAD_NAME_FULL...")
    print("\n(duplicating ROAD_NAME_FULL attribute to title attribute for caltopo.)")
    
    merged_fsrs = []
    
    # Group by ROAD_NAME_FULL - this is O(N log N) where N is FSR segments only
    for road_name, group in fsr_gdf.groupby('ROAD_NAME_FULL'):
        try:
            # Get all geometries for this FSR
            geometries = group.geometry.tolist()
            
            # Merge contiguous segments - linemerge handles the connectivity
            merged_geom = linemerge(geometries)
            
            # Calculate some statistics
            total_length = group.geometry.length.sum()
            
            merged_fsrs.append({
                'title': road_name, # caltopo likes title 
                'ROAD_NAME_FULL': road_name,  # but leave the BC attribute name also
                'ROAD_CLASS': 'resource',  # All FSRs have this
                'original_segments': len(group),
                'total_length_m': total_length,
                'geometry': merged_geom
            })
            
        except Exception as e:
            print(f"Error merging {road_name}: {e}")
            continue
    
    if not merged_fsrs:
        print("No FSR segments could be merged!")
        return None
    
    # Create new GeoDataFrame with merged FSRs
    result_gdf = gpd.GeoDataFrame(merged_fsrs, crs=fsr_gdf.crs)
    
    total_original = sum(f['original_segments'] for f in merged_fsrs)
    reduction_pct = ((total_original - len(result_gdf)) / total_original * 100)
    
    print(f"Merged {total_original} segments into {len(result_gdf)} FSR roads")
    print(f"Reduction: {reduction_pct:.1f}%")
    print(f"Average segments per FSR: {total_original / len(result_gdf):.1f}")
    
    return result_gdf

def main():
    """Main execution function"""
    # Check for input file
    geojson_file = "bc_roads.geojson"
    
    if not Path(geojson_file).exists():
        print(f"Error: {geojson_file} not found!")
        print("Please download BC road data and save as 'bc_roads.geojson'")
        return
    
    try:
        print(f"Loading {geojson_file}...")
        gdf = gpd.read_file(geojson_file)
        print(f"Loaded {len(gdf)} road segments")
        
        # Show column information
        print(f"\nDataset columns: {list(gdf.columns)}")
        print(f"CRS: {gdf.crs}")
        
        # Check for required columns
        required_cols = ['ROAD_NAME_FULL', 'ROAD_CLASS']
        missing_cols = [col for col in required_cols if col not in gdf.columns]
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}")
            print("Available columns:", list(gdf.columns))
            return
        
        # Filter for FSR segments only - this is the key optimization
        fsr_segments = filter_fsr_segments(gdf)
        
        if len(fsr_segments) == 0:
            print("No FSR segments found!")
            return
        
        # Analyze FSR data
        segment_counts = explore_fsr_data(fsr_segments)
        
        # Merge FSR segments - now only working with ~3000 segments instead of 50000
        merged_fsrs = merge_fsr_segments(fsr_segments)
        
        if merged_fsrs is not None:
            # Save results
            output_file = "bc_fsrs_merged.geojson"
            merged_fsrs.to_file(output_file, driver='GeoJSON')
            print(f"\nMerged FSR roads saved to {output_file}")
            
            # Show final statistics
            print("\nFinal Results:")
            print(f"Original FSR segments: {len(fsr_segments)}")
            print(f"Merged FSR roads: {len(merged_fsrs)}")
            print(f"Reduction: {((len(fsr_segments) - len(merged_fsrs)) / len(fsr_segments) * 100):.1f}%")
            
            # Show top 20 FSRs by segment count
            top_fsrs = merged_fsrs.nlargest(20, 'original_segments')
            print(f"\nTop 20 FSRs by original segment count:")
            for _, row in top_fsrs.iterrows():
                print(f"  {row['ROAD_NAME_FULL']}: {row['original_segments']} segments")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
