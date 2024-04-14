#!/bin/bash

make -C /mnt/data/linyanqiu/Fun_SAT/implementation/EasySAT-main

folder_path="/mnt/data/linyanqiu/Fun_SAT/implementation/EasySAT-main/dataset/2023"
file_names=$(find "$folder_path" -type f -name "*.cnf" | head -n 400)
counter=0
total_time=0
timeout_count=0
normal_count=0
declare -A run_times
declare -A exit_status_s

# 在开始处理之前删除旧的results.txt文件，确保从干净的状态开始
rm -f results.txt

process_task() {
  file_name=$1
  start_time=$(date +%s.%N)
  timeout 200s /mnt/data/linyanqiu/Fun_SAT/implementation/EasySAT-main/EasySAT "$file_name"
  exit_status=$?
  end_time=$(date +%s.%N)
  execution_time=$(awk "BEGIN {print $end_time - $start_time}")
  echo "$file_name $execution_time $exit_status" >> results.txt
}

export -f process_task
export folder_path

while read -r file_name; do
  counter=$((counter + 1))
  process_task "$file_name" &
  if (( counter % 20 == 0 )); then
    wait # 等待这一批次的任务完成
  fi
done <<< "$file_names"
wait # 确保所有后台任务都已完成

# 处理结果
while IFS= read -r line; do
  read -r file_name execution_time exit_status <<< "$line"
  run_times["$file_name"]=$execution_time
  exit_status_s["$file_name"]=$exit_status
  total_time=$(awk "BEGIN {print $total_time + $execution_time}")
  if [ $exit_status -eq 124 ]; then
    timeout_count=$((timeout_count + 1))
  else
    normal_count=$((normal_count + 1))
  fi
done < results.txt

average_time=$(awk "BEGIN {print $total_time / $counter}")

# 输出结果
counter=0
printf "\n"
echo "ALLtimes:"
for file_name in "${!run_times[@]}"; do
  counter=$((counter + 1))
  printf "[TASK%03d]%s\n" "$counter" "$file_name"
  if [ ${exit_status_s[$file_name]} -eq 124 ]; then
    echo "(T)[RUNtime]${run_times[$file_name]} s"
  else
    echo "[RUNtime]${run_times[$file_name]} s"
  fi
  printf "\n"
done
echo "TOTALtime: $total_time s"
echo "AVGtime: -$average_time s"
echo "TIMEOUTcount: $timeout_count"
echo "NORMALcount: $normal_count"