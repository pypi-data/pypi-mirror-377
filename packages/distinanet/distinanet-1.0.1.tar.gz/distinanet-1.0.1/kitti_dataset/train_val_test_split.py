import os
import argparse
from sklearn.model_selection import train_test_split

# Create the parser
parser = argparse.ArgumentParser(description='Argument parser')

# Add arguments
parser.add_argument('--annotations_csv', '-a', type=str, required=True, help='Path to KITTI annotations csv file')
parser.add_argument('--output_dir', '-o', type=str, required=True, help='Directory to output train, val and test csv files')
parser.add_argument('--train_size', type=float, default=0.7, help='Train size between 0 and 1')
parser.add_argument('--val_size', type=float, default=0.1, help='Validation size between 0 and 1')
parser.add_argument('--test_size', type=float, default=0.2, help='Test size between 0 and 1')
parser.add_argument('--random_seed', '-s', type=int, default=42, help='Path to KITTI annotation txt files')

# Parse the arguments
args = parser.parse_args()

# Set a specific random seed for reproducibility
random_seed = args.random_seed

# Define the proportions for the dataset split explicitly, including test_size
train_size = args.train_size
validation_size = args.val_size
test_size = args.test_size

print("---------train_val_test_split.csv---------")
print("Working on file",args.annotations_csv)
# Check if the sum of proportions equals 1 (100%)
if train_size + validation_size + test_size != 1:
    print("Error: The sum of train_size, validation_size, and test_size must equal 1.")
    exit()

# Load the annotations from the CSV file
annotations_file = args.annotations_csv
with open(annotations_file, 'r') as file:
    lines = file.readlines()

# Split the indices of the lines for dataset construction
line_indices = list(range(len(lines)))
train_indices, temp_indices = train_test_split(line_indices, train_size=train_size, random_state=random_seed)
validation_indices, test_indices = train_test_split(temp_indices, test_size=test_size/(test_size + validation_size), random_state=random_seed)

# Function to write specified lines to a file
def write_lines_to_file(filename, indices):
    with open(filename, 'w') as file:
        for index in indices:
            file.write(lines[index])

output_dir = args.output_dir+"/"
# Write the splits to their respective files
write_lines_to_file(output_dir+'train.csv', train_indices)
write_lines_to_file(output_dir+'validation.csv', validation_indices)
write_lines_to_file(output_dir+'test.csv', test_indices)

# Print the dataset sizes
print(f"Total dataset size: {len(lines)}")
print(f"Training set size: {len(train_indices)}")
print(f"Validation set size: {len(validation_indices)}")
print(f"Test set size: {len(test_indices)}")
