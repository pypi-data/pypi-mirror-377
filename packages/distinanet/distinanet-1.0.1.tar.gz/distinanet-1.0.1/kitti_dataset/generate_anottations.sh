#!/bin/bash

python3 kitti_to_csv.py \
    --annotations_dir 'training/label_2' \
    --classes_mapping 'classes.csv'\
    --output_csv_path 'annotations.csv' \
    --img_dir 'training/image_2' \
    --use_classnames

mkdir annotations
mv annotations.csv annotations

python3 train_val_test_split.py \
    --annotations_csv annotations/annotations.csv \
    --output_dir annotations

python3 line_converter.py \
    --train_csv annotations/train.csv \
    --val_csv annotations/validation.csv \
    --test_csv annotations/test.csv \
    --output_dir annotations \

echo "All scripts have been executed."