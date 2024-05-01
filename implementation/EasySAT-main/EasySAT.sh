#!/bin/bash

# 在开始处理之前删除旧的results.txt文件，确保从干净的状态开始
rm -f results.txt

# 编译EasySAT程序
make -C /home/ubuntu/Fun_SAT/implementation/EasySAT-main
make_exit_status=$?

# 如果 make 命令失败，则输出错误信息并终止脚本执行
if [ $make_exit_status -ne 0 ]; then
  echo "Error: make command failed. Exiting script."
  exit 1
fi

STARTtime=$(date +%s.%N)

timeout_value=1000
folder_path="/home/ubuntu/Fun_SAT/implementation/EasySAT-main/dataset/2023list1000"

# 读取目录中的前400个.cnf文件
file_names=$(find "$folder_path" -type f -name "*.cnf" | head -n 400)
counter=0
total_time=0
timeout_count=0
normal_count=0
excep_count=0

declare -A run_times
declare -A exit_status_s
declare -A sat_status_s

# 这个函数用于处理单个任务
process_task() {
  file_name=$1
  start_time=$(date +%s.%N)
  
  # 运行EasySAT并捕获输出
  output=$(timeout ${timeout_value}s /home/ubuntu/Fun_SAT/implementation/EasySAT-main/EasySAT "$file_name")
  exit_status=$?
  end_time=$(date +%s.%N)
  execution_time=$(awk "BEGIN {print $end_time - $start_time}")
  
  # 判断输出中是否包含特定字符串并记录
  if [[ "$output" == *"s SATISFIABLE"* ]]; then
    sat_status="SATISFIABLE"
  elif [[ "$output" == *"s UNSATISFIABLE"* ]]; then
    sat_status="UNSATISFIABLE"
  else
    sat_status="UNKNOWN"
  fi
  
  # 记录到results.txt
  echo "$file_name $execution_time $exit_status $sat_status" >> results.txt
}

export -f process_task
export folder_path

# 并发处理每个文件
while read -r file_name; do
  counter=$((counter + 1))
  process_task "$file_name" &
  if (( counter % 40 == 0 )); then
    wait # 等待这一批次的任务完成
  fi
done <<< "$file_names"
wait # 确保所有后台任务都已完成

# 处理结果
while IFS= read -r line; do
  read -r file_name execution_time exit_status sat_status <<< "$line"
  exit_status_s["$file_name"]=$exit_status
  sat_status_s["$file_name"]=$sat_status
  if [ $exit_status -eq 124 ]; then
    timeout_count=$((timeout_count + 1))
    run_times["$file_name"]=$((timeout_value * 2))
    total_time=$(awk "BEGIN {print $total_time + $((timeout_value * 2))}")
  fi
  if [ $exit_status -eq 134 ]; then
    excep_count=$((excep_count + 1))
    run_times["$file_name"]=$((timeout_value * 2))
    total_time=$(awk "BEGIN {print $total_time + $((timeout_value * 2))}")
  fi
  if [ $exit_status -eq 0 ]; then
    normal_count=$((normal_count + 1))
    run_times["$file_name"]=$execution_time
    total_time=$(awk "BEGIN {print $total_time + $execution_time}")
  fi
done < results.txt

average_time=$(awk "BEGIN {print $total_time / $counter}")

# 输出结果
counter=0
printf "\n"
echo "ALLtimes:"
for file_name in "${!run_times[@]}"; do
  counter=$((counter + 1))
  printf "[TASK%03d]%s %s\n" "$counter" "$file_name"
  if [ ${exit_status_s[$file_name]} -eq 124 ]; then
    echo "[TIMEOUT]${run_times[$file_name]} s"
  fi
  if [ ${exit_status_s[$file_name]} -eq 134 ]; then
    echo "[INTERRUPT]${run_times[$file_name]} s"
  fi
  if [ $exit_status -eq 0 ]; then
    echo "[RUNtime]${run_times[$file_name]} s"
  fi
  echo "[RESULT]${sat_status_s[$file_name]}"
  printf "\n"
done
echo "TOTALtime: $total_time s"
echo "AVGtime: -$average_time s"
echo "TIMEOUTcount: $timeout_count"
echo "SUCCESScount: $normal_count"
echo "INTERRUPTcount: $excep_count"

# 统计不同时间范围内的任务数量
count_100s=0
count_200s=0
count_300s=0
count_400s=0
count_500s=0
count_700s=0
count_1000s=0
count_1500s=0

for file_name in "${!run_times[@]}"; do
  execution_time=${run_times[$file_name]}
  if [ $(echo "$execution_time <= 100" | bc) -eq 1 ]; then
    count_100s=$((count_100s + 1))
  fi
  if [ $(echo "$execution_time <= 200" | bc) -eq 1 ]; then
    count_200s=$((count_200s + 1))
  fi
  if [ $(echo "$execution_time <= 300" | bc) -eq 1 ]; then
    count_300s=$((count_300s + 1))
  fi
  if [ $(echo "$execution_time <= 400" | bc) -eq 1 ]; then
    count_400s=$((count_400s + 1))
  fi
  if [ $(echo "$execution_time <= 500" | bc) -eq 1 ]; then
    count_500s=$((count_500s + 1))
  fi
  if [ $(echo "$execution_time <= 700" | bc) -eq 1 ]; then
    count_700s=$((count_700s + 1))
  fi
  if [ $(echo "$execution_time <= 1000" | bc) -eq 1 ]; then
    count_1000s=$((count_1000s + 1))
  fi
  if [ $(echo "$execution_time <= 1500" | bc) -eq 1 ]; then
    count_1500s=$((count_1500s + 1))
  fi
done

echo "100Scount: $count_100s"
echo "200Scount: $count_200s"
echo "300Scount: $count_300s"
echo "400Scount: $count_400s"
echo "500Scount: $count_500s"
echo "700Scount: $count_700s"
echo "1000Scount: $count_1000s"
echo "1500Scount: $count_1500s"

# make clean -C /home/ubuntu/Fun_SAT/implementation/EasySAT-main
# rm -f results.txt

ENDtime=$(date +%s.%N)
script_execution_time=$(awk "BEGIN {print $ENDtime - $STARTtime}")
echo "Finish in $script_execution_time s"