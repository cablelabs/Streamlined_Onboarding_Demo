#!/bin/bash
# Copyright (c) 2023 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed in accordance of the accompanied LICENSE.txt or LICENSE.md
# file in the base directory for this project. If none is supplied contact
# CableLabs for licensing terms of this software.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Path to your hostapd_cli binary
HOSTAPD_CLI=/home/pi/binaries/hostap/hostapd_cli

# These SSID and passphrase values should match what is in your hostapd configuration
# SSID=onlyatest
# PASSPHRASE=secret

sudo $HOSTAPD_CLI dpp_configurator_add
sudo $HOSTAPD_CLI dpp_qr_code $1

# SSID and passphrase are provided as hex
sudo $HOSTAPD_CLI dpp_auth_init peer=1 conf=sta-psk configurator=1 ssid=$(echo -n $SSID | xxd -p) pass=$(echo -n $PASSPHRASE | xxd -p)
