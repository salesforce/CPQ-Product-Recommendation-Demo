datetime=$(date +"%FT%H%M%S")
nohup ./job.py > "$datetime.log" 2>&1 &