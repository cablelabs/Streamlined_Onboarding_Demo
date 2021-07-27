# Streamlined_Onboarding_Demo
Resources and aggregated source for demo of Streamlined Onboarding (DPP integrated with OCF).


## Permissions
*** Must make /var/run/hostapd/wifiX readable by pi ***

## Configuration
- Change interface in demo.py to the correct wifi interface



##  Running
- Create virtual environement
	- python -m venv .
	- source bin/activate
	- pip install -r requirements.txt
- hostap websocket listener
	- python demo.py
- Flask Webpage
	- cd app
	- python webpage.py 
- Browser
	- http://pidevice:5000
