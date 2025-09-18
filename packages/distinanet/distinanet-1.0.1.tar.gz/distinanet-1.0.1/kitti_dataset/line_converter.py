import argparse
# Create the parser
parser = argparse.ArgumentParser(description='Argument parser')

# Add arguments
parser.add_argument('--train_csv', type=str, required=True, help='Path to KITTI annotations train csv file')
parser.add_argument('--val_csv', type=str, required=True, help='Path to KITTI annotations train csv file')
parser.add_argument('--test_csv', type=str, required=True, help='Path to KITTI annotations train csv file')
parser.add_argument('--output_dir', '-o', type=str, required=True, help='Directory to output train, val and test csv files')

# Parse the arguments
args = parser.parse_args()

def process_file(input_filename, output_filename):
    object_count = 0  # Initialize a counter for objects
    with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
        for line in infile:
            # Split the line into image path and object annotations
            image_path, object_annotations = line.split(' ', 1)
            # Split object annotations into individual objects
            objects = object_annotations.strip().split(' ')
            # Write each object to a new line in the output file
            for obj in objects:
                outfile.write(f"{image_path},{obj}\n")
                object_count += 1  # Increment the counter for each object
    return object_count  # Return the count of objects processed in this file

print("---------line_converter.csv---------")

# Specify the paths to the original CSV files
train_file = args.train_csv
validation_file = args.val_csv
test_file = args.test_csv

output_dir=args.output_dir+"/"

# Process each file and sum the object counts
total_objects = sum([
    process_file(train_file, output_dir+'train_objects.csv'),
    process_file(validation_file, output_dir+'validation_objects.csv'),
    process_file(test_file, output_dir+'test_objects.csv')
])

print(f"Files have been processed. Total number of objects: {total_objects}")
