# 2021 Streamlined Onboarding Demo

*Author: Andy Dolan (a.dolan@cablelabs.com)*

This repository contains the core components to execute a demonstration of
Streamlined Onboarding, the use of Wi-Fi Easy Connect (AKA Device Provisioning
Protocol or DPP) to onboard OCF Devices immediately after they are associated to
the Wi-Fi network.

A Debian-based Linux environment is assumed for this demonstration.

## Inventory of Components

This implementation of Streamlined Onboarding is made up of a number of
components that operate together at different layers and in different roles in
the architecture. Not all components are fully realized or packaged, and
executing the demo requires installation of dependencies, building of source,
configuration, and execution in a correct sequence to work correctly. The
components are available as submodules of this repository.

### Roles

For an overview of what each role in the architecture does, refer to the
Streamlined Onboarding specification (OCF), and the Wi-Fi Easy Connect
specification (WFA). The key roles that are used in this implementation are as
follows:

* OCF Onboarding tool (OBT): OCF domain root of trust; responsible for
  onboarding, provisioning, and configuring OCF Devices.
* DPP Configurator: Wi-Fi Easy Connect point of trust; responsible for
  communicating with Wi-Fi devices and associating them with the Wi-Fi network.
* DPP Diplomat: OCF Resource that is responsible for taking information from the
  DPP channel and providing it to the OBT via an OCF NOTIFY message.
* OCF Devices: OCF Devices that are to be onboarded with Streamlined Onboarding.

### Devices

To facilitate this demo, at least two Wi-Fi enabled Linux devices are needed.
These devices can be thought of in the following way:

* The access point (AP):
  * Hosts the Wi-Fi network
  * Hosts the Onboarding Tool (root of the OCF domain)
  * Hosts the Diplomat component that facilitates communications between the
    Wi-Fi and OCF layers
* The client device (client, OCF Device, station, STA):
  * The "device to be onboarded"
  * Runs a Wi-Fi client that needs to be connected to the network
  * "Displays" a QR code that can be used to start the streamlined onboarding
    process

For the sake of simplicity, this README assumes that these are the only two
devices in use, and refers to them accordingly below.

### Software Components

The software components of this demo include the following:

* SO\_IoTivity-Lite (`deps/SO_IoTivity-Lite`): The modified version of
  IoTivity-Lite, the open source standard implementation of the OCF standard,
  written in C.
  * This repository acts as the implementation of the OCF layer of components.
  * The OBT, Diplomat, and OCF Device run programs implemented with this
    IoTivity-Lite stack.
* SO\_hostap (`deps/SO_hostap`): The modified version of HostAP (`hostapd` and
  `wpa_supplicant`), the open source standard implementation of the Wi-Fi
  specification, written in C.
  * The modifications include the ability for the Wi-Fi client/enrollee/station
    to include OCF information in its DPP messages ahead of associating to the
    network via DPP.
  * The OCF Device (to be onboarded) runs an instance of `wpa_supplicant` as its
    Wi-Fi network manager.
  * The access point runs an instance of `hostapd`, which broadcasts the Wi-Fi
    network and acts as the DPP configurator.
* Streamlined\_Onboarding\_Demo (this repository): Includes the following:
  * `systemd` service definitions for `hostapd` and `wpa_supplicant` that can be
    used to automatically start and managed the modified HostAP components of
    the architecture, found in the `services/` directory.
  * Scripts that can be used to execute a basic run of DPP with `wpa_cli` and
    `hostapd_cli`, found in the `scripts/` directory.
  * Example configuration files for the HostAP components, which can be
    "installed" in a location like `/usr/local/etc/streamlined_onboarding`;
    these configurations provide the basic settings required in HostAP for DPP
    to function.
  * An IoTivity-Lite-based example OCF Device with a graphical and command line
    interface, written in Python, found in the `ocf_devices/lightswitch`
    directory.

#### Note on Web-Based OBT

Note that our modified version of IoTivity-Lite also includes a web-based
onboarding tool written in Python. This can be the primary OBT used on the
access point, or the command-line-based OBT can also be used.

However, note that, at the time of writing, the web-based OBT is not fully
merged into the primary branch of the `SO_IoTivity-Lite` repository used in this
demo, and may need to be built separately.

## Dependencies & Requirements

### Hardware and OS

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

### IoTivity-Lite and HostAP

* These repositories are available under the `deps` directory.
* See the respective guides for each of these repositories on how to build them:
  * [Getting Started guide for IoTivity-Lite](https://iotivity.org/build_linux/)
  * [`hostap` README](https://github.com/cablelabs/SO_hostap/blob/ocf_streamlined_onboarding/hostapd/README)
  * [`wpa_supplicant` README](https://github.com/cablelabs/SO_hostap/blob/ocf_streamlined_onboarding/wpa_supplicant/README)
* `hostapd` and `wpa_supplicant` must be built and configured to run on the AP
  and STA devices, respectively.
* IoTivity-Lite Devices, including the OBT, Diplomat, and simpleclient (light
  resource) can be built within the `deps/SO_IoTivity-Lite/port/linux`
  directory with `make`
* The Python-based IoTivity-Lite lightswitch defined in this repository attempts
  to build the necessary IoTivity-Lite components as part of its build process

### Python

* Use of virtual environments through `venv` or anaconda is recommended.
* Python dependencies files are available in this repository:
  * `environment.yml` provides an environment definition for use with anaconda
  * `requirements.txt` provides a list of dependencies for use with `pip`

## Overview of Building the Demo

This section provides a cursory overview of what's required to build, configure,
and run the demo from scratch. This demo assumes the use of the lightswitch
device running on a Raspberry Pi, and interacting with it via the web-based OBT.

This involves the following high-level steps:

* Ensuring the network interfaces are configured for the STA & AP devices
* Building (and optionally installing) the Wi-Fi components
  * `wpa_supplicant`
    * Additional `libwpa_client` library
  * `hostapd`
* Starting the Wi-Fi components with correct configurations
* Building the IoTivity-Lite components
  * OBT
  * Diplomat
  * Lightswitch
* Starting the AP OCF components
  * OBT (web-based)
  * Diplomat
* Initially provisioning the OCF domain
  * Onboarding the Diplomat
  * Subscribing to updates from the Diplomat
* Starting the lightswitch Device
* Executing the demo
  * Displaying a QR code on the lightswitch
  * Scanning the QR code with the web-based OBT (from a smart phone)

Not all of these steps are described in full detail, as components of this demo
are still fragmented and spread across multiple repositories.

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

## Building the Wi-Fi Components

* Generally, building the Wi-Fi components necessary for this demo involves
  updating a configuration file for compilation, compiling the source code, and
  optionally placing the resultant binaries in a known location for later use.

### `wpa_supplicant`

* `wpa_supplicant` can be built in the `deps/SO_hostap/wpa_supplicant` directory
* The `Makefile` defines the targets that can be built
* A `.config` file is required to provide additional variable definitions to
  `make` during compilation
  * An examples and explanations of each field can be found in the `defconfig`
    file
  * For use with this demo, the following variables can be used in the `.config`
    file:

```makefile
CONFIG_DRIVER_WEXT=y
CONFIG_DRIVER_NL80211=y
CONFIG_LIBNL32=y
CONFIG_DRIVER_WIRED=y
CONFIG_IEEE8021X_EAPOL=y
CONFIG_EAP_MD5=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_TLS=y
CONFIG_EAP_PEAP=y
CONFIG_EAP_TTLS=y
CONFIG_EAP_FAST=y
CONFIG_EAP_GTC=y
CONFIG_EAP_OTP=y
CONFIG_EAP_PWD=y
CONFIG_EAP_PAX=y
CONFIG_EAP_LEAP=y
CONFIG_EAP_SAKE=y
CONFIG_EAP_GPSK=y
CONFIG_EAP_GPSK_SHA256=y
CONFIG_EAP_TNC=y
CONFIG_WPS=y
CONFIG_EAP_IKEV2=y
CONFIG_PKCS12=y
CONFIG_SMARTCARD=y
CONFIG_CTRL_IFACE=y
CONFIG_SAE=y
CONFIG_BACKEND=file
CONFIG_IEEE80211W=y
CONFIG_CTRL_IFACE_DBUS_NEW=y
CONFIG_CTRL_IFACE_DBUS_INTRO=y
CONFIG_IEEE80211R=y
CONFIG_DEBUG_FILE=y
CONFIG_DEBUG_SYSLOG=y
CONFIG_IEEE80211N=y
CONFIG_IEEE80211AC=y
CONFIG_INTERWORKING=y
CONFIG_HS20=y
CONFIG_AP=y
CONFIG_P2P=y
CONFIG_WIFI_DISPLAY=y
CONFIG_IBSS_RSN=y
CONFIG_BGSCAN_SIMPLE=y
CONFIG_DPP=y
CONFIG_OCF_ONBOARDING=y
```

* With this configuration in place, the targets to compile are `wpa_supplicant`,
  `wpa_cli`, and `libwpa_client.so`
  * `wpa_supplicant` is the primary software for the Wi-Fi STA; it interacts
    with the Wi-Fi device, sending and receiving the proper messages to and from
    the AP
  * `wpa_cli` is a command line interface to interact with a running instance of
    `wpa_supplicant`, typically via a socket. This program can be used to
    execute DPP, examples of which can be seen in the `run_sta.sh` script
    [here](./scripts/hostap/run_sta.sh)
  * `libwpa_client.so` is a library that the streamlined onboarding-enabled OCF
    Devices link during their compilation; it provides the necessary commands to
    interact with `wpa_supplicant` through socket communications. Once this
    library has been compiled, it is simplest to copy it to a custom library
    directory, such as `/usr/local/lib`. The file `wpa_ctrl.h` should also be
    copied to `/usr/local/include`.

### `hostapd`

* Compiling `hostapd` is similar to compiling `wpa_supplicant` (see previous
  section)
* An example of the necessary variables to enable in the `.config` file appears
  below:

```makefile
CONFIG_DRIVER_HOSTAP=y
CONFIG_DRIVER_NL80211=y
CONFIG_LIBNL32=y
CONFIG_IAPP=y
CONFIG_RSN_PREAUTH=y
CONFIG_IEEE80211W=y
CONFIG_EAP=y
CONFIG_ERP=y
CONFIG_EAP_MD5=y
CONFIG_EAP_TLS=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_PEAP=y
CONFIG_EAP_GTC=y
CONFIG_EAP_TTLS=y
CONFIG_PKCS12=y
CONFIG_IPV6=y
CONFIG_INTERWORKING=y
CONFIG_DPP=y
CONFIG_OCF_ONBOARDING=y
```

* The targets to compile are `hostapd` and `hostapd_cli`

### Cross Compiling for Raspberry Pi

* It can be helpful to cross-compile on x86 architectures while targeting ARM
  architectures (e.g., Raspberry Pi); this enables one to compile on a more
  powerful processor and simply copy the resulting binaries to a Raspberry Pi,
  where they can still be run correctly.
* The `gcc-arm-linux-gnueabihf` package provides binaries used to compile for
  ARM architectures.
* To enable a simple means to cross compile the Wi-Fi components, add the
  following to the `.config` file for the Wi-Fi components:

```makefile
ifdef CROSS
CC=arm-linux-gnueabihf-gcc
LD=arm-linux-gnueabihf-ld
PKG_CONFIG=arm-linux-gnueabihf-pkg-config
endif
```

* The source can then be compiled for ARM architectures with the following:

```bash
make CROSS=1 <targets>
```

* Note that some libraries for the ARM architecture may not be installed by
  default for your Linux distribution; these typically need to be installed via
  `apt` and with the architecture `armhf` specified

## Starting the Wi-Fi Components

### `wpa_supplicant`

* An example configuration for `wpa_supplicant` can be found in
  `configs/hostap/so_wpa_supplicant.conf`
* `wpa_supplicant` can be run with the following command:

```
wpa_supplicant -c</path/to/config_file.conf> -i<interface_name> -d
```

### `hostapd`

* An example configuration file to use with `hostapd` can be found in
  `configs/hostap/so_hostapd.conf`
* Once compiled, `hostapd` can be run with the following command:

```
hostapd -d -i <interface_name> /path/to/hostapd_config.conf
```

## Building the OCF Components

* Generally, when building the IoTivity-Lite tools, the Makefile is located in
  `deps/SO_IoTivity-Lite/port/linux`
  * The remainder of this section assumes the use of `make` from within this
    directory
* From within this directory, the OCF examples can be built with `make <target>`

### Onboarding Tool (OBT)

* The command-line based OBT can be built in the
  `deps/SO_IoTivity-Lite/port/linux` directory with a `make SO_DPP=1 onboarding_tool`
  * Note the required environment variable `SO_DPP`, which indicates to
    different macros and definitions that code specific to streamlined
    onboarding
* Refer to the documentation on the IoTivity-Lite branch `obt-py` for
  information on building and running the web-based OBT

### Diplomat

* The diplomat can be built with `make SO_DPP=1 dpp_diplomat`

### Lightswitch

* The lightswitch device is defined in this repository, and its source code is
  located in the directory `ocf_devices/lightswitch`
* The Makefile in that directory can be used to build the necessary library that
  Python interacts with when running the lightswitch device
  * This library can be built with a simple `make` (the library is the default
    target)
* Once the lightswitch library is built, the lightswitch application can be run
  in two ways:
  * A command-line interface mode that can be run with the command `python -m
    slined_onboarding.cli.switch_cli`
  * A graphical interface (built in QT) that can be invoked with the command
    `python -m slined_onboarding.gui`
* Note that the lightswitch application relies on the `dotenv` module to read
  environment variables from a `.env` file
  * A template file with all the necessary variables (as well as some defaults
    that can be used) is available at `ocf_devices/lightswitch/dotenv_template`
  * This file can be copied to `.env` and adjusted as necessary

## Starting the AP OCF Components

### Web-Based OBT

* *TODO: More information is needed here*
* Refer to the documentation on the `obt-py` branch for information on running
  the web OBT
  * This effectively involves building a library that is then used by a Python
    executable
  * This Python program serves the web page for the OBT

### Diplomat

* Once built, the diplomat can be run with `WPA_CTRL_IFACE=/path/to/hostapd/socket_directory ./dpp_diplomat`
  * The variable `WPA_CTRL_IFACE` refers to the control socket that is created
    by and used to interact with `hostapd`
  * This socket is typically located at `/var/run/hostapd/<iface_name>` (once
    the instance of `hostapd` has been started)
  * Note that this socket may have specific permissions (e.g., to members of the
    `netdev` group on Linux), as defined in the `hostapd` configuration file
* The diplomat simply polls for information from `hostapd` and will notify
  onboarding tools that have subscribed to it for updates

## Initial Provisioning of OCF Devices

* In order for the diplomat to provide notification messages to the OBT, the OBT
  must perform three actions (as a one-time setup step):
  * Onboard the diplomat (through an owner transfer method such as just-works or
    random pin)
  * Provision an ACL to the diplomat that allows the OBT to read from the
    `/diplomat` resource
  * Subscribe to updates from the `/diplomat` through an OCF OBSERVE request
* The web OBT has the ability to discover unowned Devices through the web UI
* Once onboarded, the web UI offers means to provision an ACL (and pairwise
  credential) to allow OBT access to the `/diplomat` resource
* Once provisioned, the web OBT provides a simple toggle switch to "enable
  streamlined onboarding"
  * Activating this switch causes the OBT to send the OBSERVE request to the
    diplomat, indicating that the OBT would like to receive updates from the
    diplomat about new devices

## Starting the Lightswtich Device

* As noted above, the lightswitch device relies on the use of a `.env` file to
  set environment variables for the path to the `wpa_supplicant` control socket
* As noted above, the lightswitch device can be started in two modes:
  * The GUI lightswitch device can be started with `python -m
    slined_onboarding.gui`
  * The CLI lightswitch device can be started with `python -m
    slined_onboarding.cli.switch_cli`

## Executing the Demo

* At this point, the following devices should be running the following
  components:
  * AP/OCF administrative device:
    * `hostapd` and any necessary network software (e.g., `dnsmasq`)
    * Web-based OBT
    * Diplomat
  * Client device:
    * `wpa_supplicant` configured for a Wi-Fi interface
    * Lightswitch device
* If these devices and their software are correctly running, the demo can be run
  with the steps that follow below

### Displaying and Scanning QR Code on the Lightswitch

* The GUI form of the lightswitch offers a button that can be used to generate
  and display the DPP QR code
* The web-based OBT can be used to scan this QR code, which initiates the DPP
  authentication & configuration exchange
* Upon scanning the QR code, the client device should be associated to the Wi-Fi
  network and immediately discovered and onboarded using information it provided
  over the DPP exchange.

## Caveats and Exceptions

Note that this version of the demo is not entirely compliant with the OCF
streamlined onboarding specification, in that the information that is provided
over the DPP channel during network association does not conform to what is
outlined in the specification.

Again, further documentation is needed on building and running the web-based
OBT, as its source is distributed between the upstream OCF IoTivity-Lite
repository and the CableLabs fork of IoTivity-Lite (SO\_IoTivity-Lite).

The graphical lightswitch device is intended to be run on a Raspberry Pi 3 with
an additional Adafruit PiTFT. The source relies on specific GPIO functions that
can be "mocked" through special environment variables, so that the interface can
be run on a regular Linux desktop environment without GPIO. See the
[`dotenv_template`](/ocf_devices/lightswitch/dotenv_template) file for more
information.
