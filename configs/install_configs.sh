#!/bin/bash
CONFIG_DIR=/usr/local/etc/streamlined_onboarding
TEMP_CONFIG=/tmp/so_hostapd.conf

echo "Configuring hostapd options (these can be edited later in /usr/local/etc/streamlined_onboarding/hostapd.conf)"
read -p "Enter the interface name that hostapd should be configured to use (e.g., wlan1): " IFACE
read -p "Enter the SSID that hostapd should broadcast: " SSID
read -p "Enter the passphrase that hostapd should use: " PASSPHRASE
printf "\nConfiguration details:\nInterface: $IFACE\nSSID: $SSID \nPassphrase: $PASSPHRASE\n"
read -p "Are these details correct? (Y/n): " confirm && [[ $confirm == [nN] ]] && exit 1

echo "Installing configurations to $CONFIG_DIR"
sudo mkdir -p $CONFIG_DIR

sed -e "s/\@IFACE\@/$IFACE/g" ./hostap/so_hostapd.conf > $TEMP_CONFIG
sed -i -e "s/\@SSID\@/$SSID/g" $TEMP_CONFIG
sed -i -e "s/\@PASSPHRASE\@/$PASSPHRASE/g" $TEMP_CONFIG

sudo cp -t $CONFIG_DIR $TEMP_CONFIG ./hostap/so_wpa_supplicant.conf
rm $TEMP_CONFIG
