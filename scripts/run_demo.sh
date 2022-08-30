#!/bin/bash
#Easy TMUX to run DEMO.   Pane three is the command pane and has a menu of single key commands to run
sudo pkill -f wpa_supplicant
sudo pkill -f hostapd
sudo rfkill  block wifi
sudo rfkill unblock wifi
sleep 1
tmux new-session -d bash
tmux set -g pane-border-status top
tmux selectp -t 0    # select the first (0) pane
tmux splitw -h -p 50 # split it into two halves
tmux selectp -t 0    # select the first (0) pane
tmux splitw -v -p 50 # split it into two halves
tmux selectp -t 2    # select the new, second (2) pane
tmux splitw -v -p 50 # split it into two halves
tmux splitw -v -p 50 # split it into two halves


#0:HOSTAPD
sudo service hostapd restart
tmux select-pane -t 0 -T HOSTAPD
tmux send -t 0 "export PS1='HOSTAPD:->'" C-m
tmux send -t 0 "clear" C-m
#debug enabled
#tmux send -t 0 'sudo /usr/sbin/hostapd -d /etc/hostapd/hostapd.conf' C-m
#tmux send -t 0 'sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf' C-m
tmux send -t 0 'sudo /usr/sbin/hostapd_cli -i wlan1' C-m

#1:DIPLOMAT
tmux select-pane -t 1 -T DIPLOMAT 
tmux send -t 1 "export PS1='DIPLOMAT:->'" C-m
sleep 1
tmux send -t 1 "clear" C-m
tmux send -t 1 "cd ~/bin" C-m
tmux send -t 1 "sudo ./dpp_diplomat ./hostap_iface.conf" C-m

#2:Run AP
tmux select-pane -t 2 -T RUN_AP 
tmux send -t 2 "export PS1='AP:->'" C-m
sleep 1
tmux send -t 2 "clear" C-m
tmux send -t 2 " ~/Streamlined_Onboarding_Demo/scripts/hostap/run_ap.sh \"\"" C-m 
tmux send -t 2 "clear" C-m
tmux send -t 2 "export DISPLAY=:0" C-m
sleep 1
tmux send -t 2 "python3 ~/raspAP_TFT/tft_gui.py" C-m


#3: Control pane TO kill lamp demo
tmux select-pane -t 3 -T CONTROL 
tmux send -t 3 "export PS1='CONTORL:->'" C-m
sleep 1
tmux send -t 3 "clear" C-m
tmux send -t 3 "~/Streamlined_Onboarding_Demo/scripts/demo_command.py" C-m

#4: WEB OBT
tmux select-pane -t 4 -T WEB-OBT 
tmux send -t 4 "export PS1='OBT:->'" C-m
sleep 1
tmux send -t 4 "clear" C-m
tmux send -t 4 "sudo chown -R pi /var/run/hostapd/" C-m
#tmux send -t 4 "cd ~/SO_IoTivity-Lite/python/obt_web/" C-m
tmux send -t 4 "cd ~/bin/python/obt_web/" C-m
tmux send -t 4 "source ocf/bin/activate" C-m
tmux send -t 4 "export PYTHONFAULTHANDLER=1" C-m
tmux send -t 4 "python obt_web.py" C-m


tmux selectp -t 3    # go back to the third pane

tmux -2 attach-session -d




