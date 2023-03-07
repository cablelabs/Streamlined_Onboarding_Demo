# Building the Streamlined Onboarding Demo

## Dependencies & Requirements

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

