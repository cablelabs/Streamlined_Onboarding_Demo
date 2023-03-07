# Running the Streamlined Onboarding Demo

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


