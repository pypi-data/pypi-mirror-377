import os
import argparse
import csv
from collections import defaultdict

# Create the parser
parser = argparse.ArgumentParser(description='Argument parser')

# Add arguments
parser.add_argument('--annotations_dir', '-a', type=str, required=True, help='Path to KITTI annotation txt files')
parser.add_argument('--classes_mapping', '-c', type=str, required=True, help='Path to KITTI classes mapping csv file')
parser.add_argument('--output_csv_path', '-o', type=str, required=True, help='Path to output annotations csv path')
parser.add_argument('--img_dir', '-i', type=str, required=True,  help='Absolute path to image directory, to be added to the annotations file')
parser.add_argument('--use_classnames', '-n', action='store_true', help='Use classnames instead of class_ids')
parser.add_argument('--increment_id', '-x', action='store_true', help='Increment class_id by one (when class 0 is default background)')

# Parse the arguments
args = parser.parse_args()

# Path to the directory containing annotation files
annotations_dir = args.annotations_dir
# Path to the class mapping file
class_mapping_path = args.classes_mapping
# Output CSV file path
output_csv_path = args.output_csv_path
# Absolute path to image directory, to be added to the annotations file
abs_path = args.img_dir

# Initialize a dictionary to count occurrences of each label
label_counts = defaultdict(int)
# Data structure to hold annotation data for CSV
annotations_data = defaultdict(list)

dontcare_counts = 0

incorrect_conversions = 0

# Initialize a dictionary to map class names to class numbers
class_mapping = {}
with open(class_mapping_path, 'r') as csvfile:
    reader = csv.reader(csvfile)
    class_mapping = {rows[0]: rows[1] for rows in reader}

# Process each annotation file
for filename in sorted(os.listdir(annotations_dir)):  # Sort filenames to process in order
    if filename.endswith('.txt'):
        image_number = filename.replace('.txt', '.png')  # Prepare image number for CSV
        with open(os.path.join(annotations_dir, filename), 'r') as f:
            for line in f:
                parts = line.strip().split(' ')
                label = parts[0]
                if label == 'DontCare':
                    dontcare_counts += 1
                    continue  # Skip "DontCare" entries
                label_counts[label] += 1  # Count label occurrences
                # Extract required details for CSV
                x1, y1, x2, y2 = parts[4:8]
                z_coord = parts[13]

                if not args.use_classnames:
                    # Use class mapping to get the correct class number, default to '-1' if class not found
                    class_id = class_mapping.get(label, '-1')
                    if class_id == '-1':
                        incorrect_conversions += 1
                    else:
                        if args.increment_id:
                            class_id += 1
                else:
                    class_id = label
                
                annotations_data[image_number].append(f"{x1},{y1},{x2},{y2},{class_id},{z_coord}")

# Write annotations data to CSV
with open(output_csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    for image_number, objects in sorted(annotations_data.items()):
        # Manually join the objects with a space and construct the line
        image_path = abs_path + "/" + image_number
        line = f"{image_path} {' '.join(objects)}\n"
        csvfile.write(line)

# Sort labels by count in descending order and print
total_count = 0
sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
print("---------kitti_to_csv.csv---------")
print("Working to create file",args.output_csv_path)
if args.use_classnames:
    print("--use_classnames specified. Using classnames instead of ids in the output file.")
if args.increment_id:
    print("--increment_id specified. Incrementing class_ids by one.")
for label, count in sorted_labels:
    total_count += count
    print(f"{label}: {count}")
print(f"Total number of instances (without DontCare): {total_count}")
print(f'{dontcare_counts} DontCare instances were skipped.')
print(f'{incorrect_conversions} instances were incorrect conversions.')
