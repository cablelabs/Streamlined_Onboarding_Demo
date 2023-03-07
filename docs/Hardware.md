# Hardware Requirements and Configuration

## Hardware Requirements

* At least two independent hardware instances are required, one acting as the
  AP, one acting as the STA
* Wi-Fi adapters are required - code can be built, but will not fully run, on a
  virtual machine without a Wi-Fi adapter provided via USB passthrough
* The lightswitch Device defined in this repository is meant to be run on a
  Raspberry Pi with a configured Adafruit PiTFT (screen and buttons).
  * This accessory can be found [here](https://www.adafruit.com/product/2423)
  * This screen is not required to run the application; a graphical interface
    can be used with a mouse instead
* This repository assumes a Debian-based Linux OS

## Configuring Network Interfaces

* With Wi-Fi adapters installed/attached to a device, it is important to ensure
  that they are not managed by any pre-installed instances of `wpa_supplicant`
  or other higher-level network managers (e.g., `NetworkManager`).
* Depending on existing software on the system, there are different ways to
  approach ensuring that such devices are left alone:
  * Disabling the onboard `wpa_supplicant` service (e.g., for Raspberry Pi;
    requires use of the ethernet port for remote access to the device)
  * Enabling the special `wpa_supplicant@<interface>` systemd service by
    defining a special configuration file (e.g.,
    `/etc/wpa_supplicant/wpa_supplicant-<interface>.conf`) ensuring that the
    onboard `wpa_supplicant` only applies to a specific interface
  * See more examples [here](https://wiki.archlinux.org/title/wpa_supplicant#:~:text=wpa_supplicant%40interface.service,using%20systemd%2Dnetworkd.)
* For the AP, additional configuration and installation of other network
  components may be necessary in addition to the modified version of `hostapd`
  * The Wi-Fi adapter that will broadcast the Wi-Fi network should be configured
    with a static IP address
  * A dhcp server such as `dnsmasq` is necessary to enable assignment of IP
    addresses to newly connected devices
  * More information for basics on how to configure a networked device for
    hosting a Wi-Fi network can be found [here](https://wiki.archlinux.org/title/Software_access_point)
    * It can be helpful to follow this type of guide to run a "vanilla" Wi-Fi
      network before attempting to leverage the modified version of HostAP
      necessary for this demo.


