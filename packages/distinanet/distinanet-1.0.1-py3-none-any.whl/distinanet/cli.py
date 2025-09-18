#!/usr/bin/env python3
"""
DistinaNet CLI - unified entry point
Usage:
    distinanet train --csv_train ... --csv_val ...
    distinanet evaluate --model_path ... --csv_annotations ...
    distinanet inference --model_path ... --image_path ...
    distinanet video --model_path ... --video_path ...
"""

import sys
import argparse
import os

def print_usage():
    """Print usage information"""
    print("Usage: distinanet {train|evaluate|inference|video} [args...]")
    print("\nAvailable modes:")
    print("  train     - Train a new DistinaNet model")
    print("  evaluate  - Evaluate a trained model on test data")
    print("  inference - Run inference on a single image")
    print("  video     - Process a video file")
    print("\nFor mode-specific help, use:")
    print("  distinanet <mode> --help")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    mode = sys.argv[1]
    
    # Remove mode from args and pass the rest to the specific script
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    
    try:
        if mode == 'train':
            print("🚀 Starting training mode...")
            from distinanet.scripts.train import main as train_main
            train_main()
        elif mode == 'evaluate':
            print("🔍 Starting evaluation mode...")
            from distinanet.scripts.test import main as eval_main
            eval_main()
        elif mode == 'inference':
            print("📸 Starting inference mode...")
            from distinanet.scripts.inference import main as inference_main
            inference_main()
        elif mode == 'video':
            print("🎥 Starting video processing mode...")
            from distinanet.scripts.video import main as video_main
            video_main()
        else:
            print(f"❌ Unknown mode: {mode}")
            print_usage()
            sys.exit(1)
    except ImportError as e:
        print(f"❌ Error importing module for mode '{mode}': {e}")
        print("Make sure DistinaNet is properly installed with 'pip install .'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running {mode}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
