# Hardware Requirements and Configuration

## Hardware Requirements

* At least two independent hardware instances are required, one acting as the
  AP, one acting as the STA
* Wi-Fi adapters are required - code can be built, but will not fully run, on a
  virtual machine without a Wi-Fi adapter provided via USB passthrough
* The client Devices defined in this repository are meant to be run on Raspberry
  Pis with a configured Adafruit PiTFT (screen and buttons).
  * This accessory can be found [here](https://www.adafruit.com/product/2423)
  * This physical buttons are not required to run the application; the graphical
    interfaces can be used with a mouse instead
* This repository assumes a Debian-based Linux OS

## Configuring Network Interfaces & Networking Software

* With Wi-Fi adapters installed/attached to a device, it is important to ensure
  that they are not managed by any pre-installed instances of `wpa_supplicant`
  or other higher-level network managers (e.g., `NetworkManager`).

### Client (Station) Wi-Fi Configuration

* Depending on existing software on the system, there are different approaches
  to ensure that the correct (modified) version of `wpa_supplicant` is used:
* At its simplest, replacing the `wpa_supplicant` binary
  (`/sbin/wpa_supplicant`) with the modified version (or a symlink to the
  modified version)
  * A Raspberry Pi's default configuration of `dhcpcd` will invoke this
    `wpa_supplicant` binary for each wireless interface
* Alternatively, here are a few approaches to leverage the modified version
  selectively on different wireless interfaces:
  * Adding the `nohook wpa_supplicant` line to an interface's clause in
    `/etc/dhcpcd.conf`
  * Disabling the onboard `wpa_supplicant` service (e.g., for Raspberry Pi;
    requires use of the ethernet port for remote access to the device)
  * Enabling the special `wpa_supplicant@<interface>` systemd service by
    defining a special configuration file (e.g.,
    `/etc/wpa_supplicant/wpa_supplicant-<interface>.conf`) ensuring that the
    onboard `wpa_supplicant` only applies to a specific interface
  * See more examples [here](https://wiki.archlinux.org/title/wpa_supplicant#:~:text=wpa_supplicant%40interface.service,using%20systemd%2Dnetworkd.)

### Access Point Wi-Fi Configuration

* Note that, this demo is also anticipated to be run with the NetReach access
  point, available [here](https://github.com/cablelabs/micronets-gw/releases/tag/v1.2.1-nccoe)
  * If leveraging this version, disregard instructions in this documentation on
    the configuration of the AP.
* For the AP, additional configuration and installation of other network
  components may be necessary in addition to the modified version of `hostapd`
* The Wi-Fi adapter that will broadcast the Wi-Fi network should be configured
  with a static IP address
* A DHCP server such as `dnsmasq` is necessary to enable assignment of IP
  addresses to newly connected devices
* More information for basics on how to configure a networked device for hosting
  a Wi-Fi network can be found [here](https://wiki.archlinux.org/title/Software_access_point)
  * It can be helpful to follow this type of guide to run a "vanilla" Wi-Fi
    network before attempting to leverage the modified version of HostAP
    necessary for this demo.
