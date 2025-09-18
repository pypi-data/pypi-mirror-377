#!/bin/bash

# Define the URLs
url1="https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_image_2.zip"
url2="https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_label_2.zip"

# Download the files
wget $url1 -O data_object_image_2.zip
wget $url2 -O data_object_label_2.zip

# Unzip the files in the same folder
unzip data_object_image_2.zip
unzip data_object_label_2.zip
