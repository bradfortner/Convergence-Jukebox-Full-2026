
import os
import wordsegment
import csv

# Load the wordsegment library
wordsegment.load()

# Set the directory containing the files
directory = "rockabilly"

# Create a list to hold the filename pairs
filename_pairs = []

# Iterate over the files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".mp3"):
        # Separate the filename from the extension
        name, extension = os.path.splitext(filename)
        
        # Segment the filename into words
        segmented_name = ' '.join(wordsegment.segment(name))
        
        # Create the new filename
        new_filename = f"{segmented_name}{extension}"
        
        # Add the original and new filenames to the list
        filename_pairs.append([filename, new_filename])

# Write the filename pairs to a CSV file
with open('suggested_renames.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Original Filename', 'Suggested New Filename'])
    writer.writerows(filename_pairs)

print("CSV file 'suggested_renames.csv' created successfully.")
