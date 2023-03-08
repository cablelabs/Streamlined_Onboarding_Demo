# Streamlined Onboarding Demo

*Author: Andy Dolan (a.dolan@cablelabs.com)*

## Documentation Manifest

* `README.md` (this file): Overview of demo components
* [`docs/Hardware.md`](./docs/Hardware.md): Hardware requirements &
  configuration
* [`docs/Build.md`](./docs/Build.md): How to build demo components
* [`docs/Running.md`](./docs/Running.md): How to run each component and execute
  the demo

## Overview

This repository contains the core components to execute a demonstration of
Streamlined Onboarding, the use of Wi-Fi Easy Connect (AKA Device Provisioning
Protocol or DPP) to onboard OCF Devices immediately after they are associated to
the Wi-Fi network.

A Debian-based Linux environment is assumed for this demonstration.

![Figure 1: Overview of Streamlined Onboarding Flow](./docs/Streamlined_Onboarding_Overview_Architecture.png)

The general flow of the streamlined onboarding demo is pictured above; its
general steps are as follows:

1. The user scans the Easy Connect QR code (containing the Easy Connect URI)
   presented by the client OCF device.
2. The system (or user) presents the Easy Connect URI to the Easy connect
   Configurator.
3. Network-layer onboarding occurs:
   1. The Configurator starts the Easy Connect onboarding.
   2. As part of the Easy Connect configuration request, the client device
      provides its OCF UUID & simple secret.
   3. Upon reception, the Easy Connect Configurator relays the client's OCF
      information to the Diplomat (black arrow).
   4. Once the client device has connected to the network, the diplomat provides
      the client's OCF information to the OBT (thin, solid, blue arrow).
4. The OBT performs automated discovery of the client device, filtered to the
   client's UUID.
5. When the client device responds to discovery, the OBT onboards it, leveraging
   the simple secret provided over the network-layer onboarding.

The diagram above displays two client devices, a lamp and a light switch. Once
both client devices are onboarded through this method, a final step of
provisioning access between the two so that the switch can operate on the lamp
is performed through the OBT.

## Inventory of Components

This implementation of Streamlined Onboarding is made up of a number of
components that operate together at different layers and in different roles in
the architecture. Not all components are fully realized or packaged, and
executing the demo requires installation of dependencies, building of source,
configuration, and execution in a correct sequence to work correctly. The
necessary dependencies are available as submodules of this repository.

### Roles

For an overview of what each role in the architecture does, refer to the
Streamlined Onboarding specification (OCF), and the Wi-Fi Easy Connect
specification (WFA). The key roles that are used in this implementation are as
follows:

* OCF Onboarding tool (OBT): OCF domain root of trust; responsible for
  onboarding, provisioning, and configuring OCF Devices. For this demo, one of
  two options exist for the OBT:
  * The standard CLI-based OBT, buildable from within
    `deps/SO_IoTivity-Lite/port/linux`
  * The Web-based OBT, available on the `obt-py` branch of
    `deps/SO_IoTivity-Lite`
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
* The client device(s) (client, OCF Device, station, STA):
  * The "device to be onboarded"
  * Runs a Wi-Fi client that needs to be connected to the network
  * "Displays" a QR code that can be used to start the streamlined onboarding
    process

For the sake of simplicity, this README generally assumes that these are the
only two devices in use, and refers to them accordingly below.

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
  * Note that these changes are also available in the [Net Reach/Micronets
    version]
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
