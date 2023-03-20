# Running the Streamlined Onboarding Demo

## Overview

This guide provides instructions on how to run the various components of the
streamlined onboarding demo, as well as how to execute the demo. Here is an
overview of the required steps:

* Starting the Wi-Fi components with correct configurations
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

## Starting the Wi-Fi Components

### `hostapd`

If leveraging the NetReach variant of the AP Wi-Fi components, skip this
subsection.

* An example configuration file to use with `hostapd` can be found in
  `configs/hostap/so_hostapd.conf`
* Once compiled, `hostapd` can be run with the following command:

```
hostapd -d -i <interface_name> /path/to/hostapd_config.conf
```

### `wpa_supplicant`

* An example configuration for `wpa_supplicant` can be found in
  `configs/hostap/so_wpa_supplicant.conf`
* `wpa_supplicant` can be run with the following command:

```
wpa_supplicant -c</path/to/config_file.conf> -i<interface_name> -d
```

On Raspberry Pis, `/sbin/wpa_supplicant` is invoked via the `dhcpcd` service;
replacing the `wpa_supplicant` binary as recommended in the [build
documentation](./Build.md#recommended-installation-paths) is sufficient for
automatic invocation. The default `wpa_supplicant` configuration file is
`/etc/wpa_supplicant/wpa_supplicant.conf`. The recommended settings to include
in the `wpa_supplicant.conf` file are as follows:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=0
country=US
pmf=2
dpp_config_processing=2
```

Note that the `update_config=0` setting ensures that Wi-Fi network information
does not persist across instances of `wpa_supplicant`. This is useful for
repeatedly testing the demo, for which the Wi-Fi stack simply needs to be
restarted (instead of needing to delete the `network` block from the
configuration file each time).

## Starting the AP OCF Components

### Diplomat

* Once built, the diplomat can be run with `WPA_CTRL_IFACE=/path/to/hostapd/socket_directory DHCP_NAMED_PIPE=/path/to/lease_notify/file /path/to/dpp_diplomat`
  * The variable `WPA_CTRL_IFACE` refers to the control socket that is created
    by and used to interact with `hostapd`
    * This socket is typically located at `/var/run/hostapd/<iface_name>` (once
      the instance of `hostapd` has been started)
    * Note that this socket may have specific permissions (e.g., to members of
      the `netdev` group on Linux), as defined in the `hostapd` configuration
      file
  * The variable `DHCP_NAMED_PIPE` refers to the DHCP leases notification named
    pipe to which the AP's installation of `dnsmasq` should provide DHCP lease
    information.
    * In its current version, this variable MUST be `/var/run/diplomat/leases`
* Alternatively, use the `diplomat.service` `systemd` service to start the
  diplomat (including at boot time).
  * The necessary environment variables are configured in the service file's
    definition (`/etc/systemd/system/diplomat.service`).
* The diplomat operates in the following way:
  * The diplomat first polls for information from `hostapd`.
  * Once such information is received, the diplomat polls the DHCP notification
    named pipe for indication that a device has been assigned a network address.
  * Once DHCP information is received from the named pipe, the diplomat notifies
    onboarding tools that have subscribed to it for updates.

### Web-Based OBT

*Note that this subsection is optional, and the CLI-based OBT can be used
instead of the web-based OBT.*

* *TODO: More information is needed here*
* Refer to the documentation on the `obt-py` branch of IoTivity-Lite for
  information on running the web OBT
  * This effectively involves building a library that is then used by a Python
    executable
  * This Python program serves the web page for the OBT

## Initial Provisioning of Diplomat

* In order for the diplomat to provide notification messages to the OBT, the OBT
  must perform three actions (as a one-time setup step):
  * Onboard the diplomat (through an owner transfer method such as just-works or
    random pin)
  * Provision an ACL to the diplomat that allows the OBT to read from the
    `/diplomat` resource
  * Subscribe to updates from the `/diplomat` resource through an OCF OBSERVE
    request

### CLI-Based OBT

Using the CLI-based OBT, the diplomat can be onboarded & provisioned using the
following steps:

* Discover unowned devices (option `1`)
* Onboard with Just Works (option `8`)
  * Select the `DPP Diplomat` for the device to onboard
* Provision ACE2 (option `13`)
  * Device selection: `DPP Diplomat`
  * Subject: `(OBT)`
  * Number of resources in this ACE: `1`
  * Have resource href: `1 (Yes)`
  * Enter resource href: `/diplomat`
  * Permissions: `1` (Yes) for each of `CREATE`, `RETRIEVE`, `UPDATE`, `DELETE`,
    `NOTIFY`
* Observe Diplomat (option `41`)

### Web-Based OBT

* The web OBT has the ability to discover unowned Devices through the web UI
* Once onboarded, the web UI offers means to provision an ACL (and pairwise
  credential) to allow OBT access to the `/diplomat` resource
* Once provisioned, the web OBT provides a simple toggle switch to "enable
  streamlined onboarding"
  * Activating this switch causes the OBT to send the OBSERVE request to the
    diplomat, indicating that the OBT would like to receive updates from the
    diplomat about new devices

## Starting the Client Devices

### Running Locally (From Source)

* Note that the client applications rely on the `dotenv` module to read
  environment variables from a `.env` file
  * A template file with all the necessary variables (as well as some defaults
    that can be used) is available at `ocf_devices/dotenv_template`
  * This file can be copied to `.env` and adjusted as necessary
  * As documented in the [build instructions](./Build.md#recommended-installation-paths),
    this environment file should be copied to
    `/etc/opt/streamlined_onboarding/prod.env` for a production system.
* Once the `libso.so` library is built, the client applications can be run by
  invoking the following (from within the `ocf_devices` directory):
  * To run the lamp device, use `python -m slined_onboarding.lamp`
  * To run the lightswitch device, use `python -m slined_onboarding.lightswitch`

### Running from Installed Module

The GUIs can be invoked using `python -m slined_onboarding.(lamp|lightswitch)`.

Note that, when doing so, the environment variables in the [`dotenv_template`](../ocf_devices/dotenv_template)
must be defined, so a full invocation may look like the following:

```sh
SO_IFACE=wlan0 WPA_CTRL_IFACE=/var/run/wpa_supplicant/wlan0 SO_LIGHTSWITCH_CREDS=/var/opt/streamlined_onboarding/lightswitch_creds SO_LAMP_CREDS=/var/opt/streamlined_onboarding/lamp_creds python -m slined_onboarding.lamp
```

Which can be further simplified to the following, when using a `.env` file:

```sh
# Export variables for subsequent commands
set -a
# Read environment variables from .env file
source /etc/opt/streamlined_onboarding/prod.env
# Invoke application
python -m slined_onboarding.lamp
```

See the [autostart files](../ocf_devices/autostart) for example invocations.

## Executing the Demo

* Once all components are configured and started, the following devices should
  be running the following components:
  * AP/OCF administrative device:
    * `hostapd` and any necessary network software (e.g., `dnsmasq`)
    * OBT (CLI or web-based)
    * DPP Diplomat
  * Client device(s):
    * `wpa_supplicant` with proper configuration
    * Client Python GUI

### Displaying and Scanning QR Code on the Lightswitch

* The GUI clients offer a button that can be used to generate and display the
  DPP QR code.
* This DPP URI is then provided to the DPP configurator on the AP, which can
  take place in a few different ways:
  * The URI is manually copied/pasted into an instance of `hostapd_cli` on the
    configurator.
  * The URI is provided to a cloud-based network controller (e.g., NetReach).
  * The web-based OBT can be used to scan the client's QR code, which in turn
    provides the URI to `hostapd`.
* Once the DPP URI is provided to the configurator, the client device should be
  associated to the Wi-Fi network and, once it has been assigned a network
  address via DHCP, immediately discovered and onboarded by the OBT using
  information it provided over the DPP exchange.
