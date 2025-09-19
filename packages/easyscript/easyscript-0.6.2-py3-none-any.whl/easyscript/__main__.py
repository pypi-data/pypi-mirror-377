#!/usr/bin/env python3
"""
EasyScript Command Line Interface

This module provides command-line execution capabilities for EasyScript files.
It can be invoked using:
    python -m easyscript <file.es>
    py -m easyscript <file.es>
"""

import sys
import argparse
import os
from pathlib import Path
from .easyscript import EasyScriptEvaluator


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        prog='easyscript',
        description='EasyScript - A simple scripting language that blends Python and JavaScript syntax',
        epilog='Example: python -m easyscript script.es'
    )
    
    parser.add_argument(
        'file', 
        help='EasyScript file to execute (.es extension recommended)'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.5.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # argparse calls sys.exit() on error or help
        return
    
    # Check if file exists
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Read the EasyScript file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
    except UnicodeDecodeError:
        print(f"Error: Could not read '{args.file}' as UTF-8 text.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Executing EasyScript file: {args.file}")
        print(f"File size: {len(code)} characters")
    
    # Create evaluator and execute the code
    try:
        evaluator = EasyScriptEvaluator()
        result = evaluator.evaluate(code)
        
        # For script execution, don't print the final result since log() statements
        # already print their output. Only print non-None results that aren't from log() calls.
        # This prevents duplicate output from log() functions.
        
    except Exception as e:
        print(f"Error executing EasyScript: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()