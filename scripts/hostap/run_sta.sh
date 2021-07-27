#!/bin/bash

WPA_CLI=/home/adolan/Projects/hostap/wpa_supplicant/wpa_cli

# Example of manually adding OCF information via wpa_cli
# sudo $WPA_CLI dpp_ocf_info_add uuid=46fc939f-ced7-48fd-6da4-c9837ab85794 cred=ogEEIFggUdEWVi5HYglfqF3GNkT8N+QEvIMa+NpsTUNZcqK1qnY=

sudo $WPA_CLI dpp_bootstrap_gen type=qrcode mac=18d6c70f76c3 chan=81/1
echo
# Copy the DPP URI that is output from this command
sudo $WPA_CLI dpp_bootstrap_get_uri 1
echo
sudo $WPA_CLI dpp_listen 2412
