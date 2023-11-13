#!/bin/bash

# Check if an argument was provided
if [ $# -eq 0 ]; then
  echo "Usage: $0 extension"
  exit 1
fi

# The output file.
output=$1
# The extension to search for, provided as the first command-line argument.
extension=$2
# The directory to start searching from.
start_dir="."

# Clear the output file in case it already exists.
> "$output"

# Use find to recursively get all files with the given extension.
# Read the results into a while loop.
find "$start_dir" -type f -name "*.$extension" -print0 | while IFS= read -r -d '' file; do
    # Skip the output file if it is encountered in the find results.
    if [[ "$file" == *"$output" ]]; then
        continue
    fi
    # Append the filename to the output file.
    echo "==> $file <==" >> "$output"
    # Append the file content to the output file.
    cat "$file" >> "$output"
    # Optionally, append a separator between files.
    echo -e "\n" >> "$output"
done

# Move the temporary file to the final output to avoid including it in the find results.
mv "$output" "${start_dir}/$output"
