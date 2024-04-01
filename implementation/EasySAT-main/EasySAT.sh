#!/bin/bash

folder_path="/mnt/data/linyanqiu/funsearch_sat_cpp/implementation/EasySAT-main/dataset/test"
file_names=$(find "$folder_path" -type f -name "*.cnf" | head -n 2)
counter=0
total_time=0

while read -r file_name; do
  counter=$((counter + 1))
  printf "=======#%03d=======%s\n" "$counter" "$file_name"
  start_time=$(date +%s.%N) 
  # timeout 100s /mnt/data/linyanqiu/funsearch_sat_cpp/implementation/EasySAT-main/EasySAT $file_name
  /mnt/data/linyanqiu/funsearch_sat_cpp/implementation/EasySAT-main/EasySAT $file_name
  end_time=$(date +%s.%N)

  execution_time=$(awk "BEGIN {print $end_time - $start_time}")
  echo "runtime: $execution_time s"
  total_time=$(awk "BEGIN {print $total_time + $execution_time}")
  echo "=================="
done <<< "$file_names"
average_time=$(awk "BEGIN {print $total_time / $counter}")

echo "TOTALtime: $total_time s"
echo "AVGtime: -$average_time s"