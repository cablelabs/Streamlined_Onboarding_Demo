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

WPA_CLI=/home/adolan/Projects/hostap/wpa_supplicant/wpa_cli

# Example of manually adding OCF information via wpa_cli
# sudo $WPA_CLI dpp_ocf_info_add uuid=46fc939f-ced7-48fd-6da4-c9837ab85794 cred=ogEEIFggUdEWVi5HYglfqF3GNkT8N+QEvIMa+NpsTUNZcqK1qnY=

sudo $WPA_CLI dpp_bootstrap_gen type=qrcode mac=18d6c70f76c3 chan=81/1
echo
# Copy the DPP URI that is output from this command
sudo $WPA_CLI dpp_bootstrap_get_uri 1
echo
sudo $WPA_CLI dpp_listen 2412
