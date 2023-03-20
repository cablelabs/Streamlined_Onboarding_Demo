# Streamlined Onboarding Demo Deployment for Raspberry Pi

This document provides a brief summary of how to deploy the streamlined
onboarding demo on a set of Raspberry Pis. This guide assumes the use of the
NetReach AP components (`hostapd`, `dnsmasq` with lease notification script).
Refer to the [NetReach release documentation](https://github.com/cablelabs/micronets-gw/releases/tag/v1.2.1-nccoe)
for details on installing those components.

This configuration is consistent with the lab environment used for the 2023
NCCoE IoT Onboarding project. This guide provides high-level steps; for more
specifics, refer to the other [documentation](https://github.com/cablelabs/Streamlined_Onboarding_Demo/tree/master/docs)
in the Streamlined Onboarding Demo repository.

## Hardware Setup Summary

This demo's hardware configuration consists of 3 Raspberry Pis, each with a
compatible Wi-Fi adapter (e.g., Atheros AR9271), running at least
Debian/Raspberry Pi OS 10:

* Access Point (AP): Can be headless (no GUI/Desktop Environment)
  * See [NetReach documentation]() for instructions on initial configuration.
* Client Pis (2):
  * Raspberry Pi OS with Desktop
  * [Adafruit PiTFT](https://www.adafruit.com/product/2423) installed &
    configured (see product support for details).

It is recommended that the onboard Wi-Fi adapter on each Pi be disabled. This
can be achieved by adding `dtoverlay=disable-wifi` to the Pi's `config.txt`
file (see [documentation](https://www.raspberrypi.com/documentation/computers/config_txt.html#what-is-config-txt)).

With the onboard adapter disabled, the Pi should have only a single Wi-Fi
interface, which this guide will assume is referred to as `wlan0`.

## Component Installation

See the [build documentation](https://github.com/cablelabs/Streamlined_Onboarding_Demo/blob/master/docs/Build.md)
for a summary of installation paths of each component.

### Access Point

For installation of Wi-Fi components of the AP Pi, refer to the [NetReach
documentation]().

The following steps should be taken to install the streamlined onboarding
components on the AP Pi:

1. Install the following binaries to `/opt/streamlined_onboarding`:
   * `onboarding_tool`
   * `dpp_diplomat`
2. Create the credentials directories for the OBT & Diplomat (also in
   `/opt/streamlined_onboarding`):
   * `onboarding_tool_creds`
   * `dpp_diplomat_creds`
3. Install the `systemd` service for the DPP Diplomat:
   * Install `diplomat.service` to `/etc/systemd/system`
   * Run `systemctl daemon-reload` (as root/with `sudo`)
   * Optionally enable the diplomat service to run on boot with `systemctl
     enable diplomat.service` (as root/with `sudo`).

The following snippet performs all of the steps described above (assumes use of
`sudo` and that all necessary files are in current working directory):

```sh
export INSTALL_DEST=/opt/streamlined_onboarding
sudo mkdir -p $INSTALL_PREFIX/{onboarding_tool,dpp_diplomat}_creds
sudo install -t $INSTALL_PREFIX onboarding_tool dpp_diplomat
sudo install -m 644 diplomat.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable diplomat.service
unset -v INSTALL_DEST
```

### Client Pis

This guide assumes the use of the modified `wpa_supplicant` included in this
repository (and release). However, the NetReach variant may also be used.

The following steps should be taken to install the streamlined onboarding
components on the client Pis:

1. Install the modified Wi-Fi components to `/opt/streamlined_onboarding` and
   create symlink in `/usr/sbin`:
   * Install `wpa_supplicant` to `/opt/streamlined_onboarding`
   * Install `wpa_cli` to `/opt/streamlined_onboarding`
   * Stop `dhcpcd` service with `sudo systemctl stop dhcpcd.service`
   * Back up system-installed `/usr/sbin/wpa_supplicant` (to, e.g.,
     `/usr/sbin/wpa_supplicant.orig`)
   * Back up system-installed `/usr/sbin/wpa_cli` (to, e.g.,
     `/usr/sbin/wpa_cli.orig`)
   * Create symlink to modified supplicant & components in `/usr/sbin` using the
     following commands:
     ```sh
     sudo ln -s /opt/streamlined_onboarding/wpa_supplicant /usr/sbin
     sudo ln -s /opt/streamlined_onboarding/wpa_cli /usr/sbin
     ```
   * Restart `dhcpcd` with `sudo systemctl restart dhcpcd.service`
2. Install modified Wi-Fi libraries leveraged by client applications:
   * Install `libwpa_client.so` to `/usr/local/lib`
   * Install `wpa_ctrl.h` to `/usr/local/include`
3. Install Python client module
   * Install system dependency `python3-pyqt5` via `apt`
   * Install client module from wheel package with, e.g. `pip install
     ./so_demo-0.0.2-py3-none-any.whl`
   * Install client application environment file (e.g., `dotenv_template`) to
     `/etc/opt/streamlined_onboarding/prod.env`
   * Optionally install the autostart `*.desktop` file(s) to
     `/home/pi/.config/autostart`.
     * To enable the autostart file, remove line 2 (`Hidden=true`) for only ONE
       `.desktop` file.

The following snippet performs all of the steps described above, again assuming
that all necessary files are located in the current working directory:

```sh
#!/bin/bash
export INSTALL_DEST=/opt/streamlined_onboarding CONFIG_DEST=/etc/opt/streamlined_onboarding
sudo mkdir -p $INSTALL_DEST $CONFIG_DEST
mkdir -p $HOME/.config/autostart

 # Wi-Fi components
sudo install -t $INSTALL_DEST wpa_{supplicant,cli}
sudo systemctl stop dhcpcd.service
sudo mv /usr/sbin/wpa_supplicant{,.orig}
sudo mv /usr/sbin/wpa_cli{,.orig}
sudo ln -s $INSTALL_DEST/wpa_supplicant /usr/sbin
sudo ln -s $INSTALL_DEST/wpa_cli /usr/sbin
sudo systemctl restart dhcpcd.service

 # Wi-Fi libraries
sudo install -m 644 libso.so /usr/local/lib
sudo install -m 644 wpa_ctrl.h /usr/local/include

 # Python client module
sudo apt update && sudo apt install -y python3-pyqt5
pip install ./so_demo-0.0.2-py3-none-any.whl
sudo install -m 644 dotenv_template $CONFIG_DEST/prod.env
install -m 644 -t $HOME/.config/autostart {lightswitch,lamp}.desktop

 # Cleanup
unset -v INSTALL_DEST CONFIG_DEST
```
