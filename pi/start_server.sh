nohup python3 -u /home/pi/ai-car/control_server.py >> /home/pi/ai-car/log/control_server.log 2>&1 & echo $! > /home/pi/ai-car/log/control_pid.txt
nohup python3 -u /home/pi/ai-car/stream_server.py >> /home/pi/ai-car/log/stream_server.log 2>&1 & echo $! > /home/pi/ai-car/log/stream_pid.txt
