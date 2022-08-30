#!/bin/bash

# Path to your hostapd_cli binary
HOSTAPD_CLI=/usr/sbin/hostapd_cli

# These SSID and passphrase values should match what is in your hostapd configuration
 SSID=IOT
 PASSPHRASE=secureyouriot

#sudo $HOSTAPD_CLI dpp_configurator_add
#sudo $HOSTAPD_CLI dpp_qr_code $1

# SSID and passphrase are provided as hex
sudo $HOSTAPD_CLI dpp_auth_init peer=1 conf=sta-psk configurator=1 ssid=$(echo -n $SSID | xxd -p) pass=$(echo -n $PASSPHRASE | xxd -p)
