# Streamlined_Onboarding_Demo
Resources and aggregated source for demo of Streamlined Onboarding (DPP integrated with OCF).


## Permissions
. Must make /var/run/hostapd/wifiX readable by pi


== Running
- Create virtual environement
	- python -m venv .
- hostap websocket listener
	- python demo.py
- Flask Webpage
	- cd app
	- python webpage.py 
