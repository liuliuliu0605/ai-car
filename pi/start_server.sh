nohup python3 -u control_server.py >> log/control_server.log 2>&1 & echo $! > log/control_pid.txt
nohup python3 -u stream_server.py >> log/stream_server.log 2>&1 & echo $! > log/stream_pid.txt
