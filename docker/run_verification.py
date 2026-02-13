#!/usr/bin/env python
"""
Entrypoint script for running single ConStrain verification cases in Docker.
Accepts a verification case JSON file path and configuration parameters.
"""
import sys
import os
import json
import argparse
from constrain.api import Verification, VerificationCase


def main():
    parser = argparse.ArgumentParser(
        description='Run a single ConStrain verification case',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run verification with default settings
  python run_verification.py /app/workflows/verification_case.json
  
  # Run with custom output path
  python run_verification.py /app/workflows/case.json --output /app/results
  
  # Run with custom library path
  python run_verification.py /app/workflows/case.json --lib-items /app/custom_lib.json
        """
    )
    
    parser.add_argument(
        'case_file',
        help='Path to the verification case JSON file'
    )
    
    parser.add_argument(
        '--output',
        default='/app/results',
        help='Output directory for verification results (default: /app/results)'
    )
    
    parser.add_argument(
        '--lib-items',
        default='./schema/library.json',
        help='Path to library items JSON file (default: ./schema/library.json)'
    )
    
    parser.add_argument(
        '--data',
        help='Path to preprocessed data CSV file (optional)'
    )
    
    parser.add_argument(
        '--plot-option',
        choices=['all-compact', 'all-expand', 'day-compact', 'day-expand'],
        default='all-compact',
        help='Type of plots to generate (optional)'
    )
    
    parser.add_argument(
        '--fig-size',
        default='6.4,4.8',
        help='Figure size as width,height (default: 6.4,4.8)'
    )
    
    parser.add_argument(
        '--tolerances',
        help='Path to custom tolerances JSON file (optional)'
    )
    
    args = parser.parse_args()
    
    # Validate case file exists
    if not os.path.exists(args.case_file):
        print(f"Error: Verification case file not found: {args.case_file}")
        sys.exit(1)
    
    # Validate output directory exists
    if not os.path.exists(args.output):
        print(f"Creating output directory: {args.output}")
        os.makedirs(args.output, exist_ok=True)
    
    # Validate library file exists
    if not os.path.exists(args.lib_items):
        print(f"Error: Library items file not found: {args.lib_items}")
        sys.exit(1)
    
    # Parse figure size
    try:
        fig_width, fig_height = map(float, args.fig_size.split(','))
        fig_size = (fig_width, fig_height)
    except:
        print(f"Error: Invalid figure size format: {args.fig_size}")
        print("Expected format: width,height (e.g., 6.4,4.8)")
        sys.exit(1)
    
    print(f"Loading verification case from: {args.case_file}")
    
    # Load the verification case
    try:
        verification_case = VerificationCase(json_case_path=args.case_file)
    except Exception as e:
        print(f"Error loading verification case: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"Creating Verification object...")
    
    # Create verification object
    try:
        verification = Verification(verifications=verification_case)
    except Exception as e:
        print(f"Error creating Verification object: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Load preprocessed data if provided
    preprocessed_data = None
    if args.data:
        if not os.path.exists(args.data):
            print(f"Warning: Data file not found: {args.data}")
            print("Continuing without preprocessed data...")
        else:
            print(f"Loading preprocessed data from: {args.data}")
            try:
                from constrain.api import DataProcessing
                data_processing = DataProcessing(
                    data_path=args.data,
                    data_source="EnergyPlus"
                )
                preprocessed_data = data_processing.data
            except Exception as e:
                print(f"Warning: Could not load data file: {e}")
                print("Continuing without preprocessed data...")
    
    print(f"Configuring verification...")
    
    # Configure verification
    try:
        config_kwargs = {
            'output_path': args.output,
            'lib_items_path': args.lib_items,
            'plot_option': args.plot_option,
            'fig_size': fig_size,
            'num_threads': 1,
            'preprocessed_data': preprocessed_data,
        }
        
        if args.tolerances:
            config_kwargs['path_to_custom_tolerance_file'] = args.tolerances
        
        verification.configure(**config_kwargs)
    except Exception as e:
        print(f"Error configuring verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"Running verification cases...")
    
    # Run verification
    try:
        verification.run()
        print(f"\n✓ Verification completed successfully!")
        print(f"Results saved to: {args.output}")
    except Exception as e:
        print(f"\nError running verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
