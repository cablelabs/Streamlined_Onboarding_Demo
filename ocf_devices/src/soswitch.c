/*
  Copyright (c) 2023 Cable Television Laboratories, Inc. ("CableLabs")
                     and others.  All rights reserved.

  Licensed in accordance of the accompanied LICENSE.txt or LICENSE.md
  file in the base directory for this project. If none is supplied contact
  CableLabs for licensing terms of this software.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

#include "oc_api.h"
#include "port/oc_clock.h"
#include "ocf_dpp.h"
#include "soswitch.h"
#include "socommon.h"
#include <stdio.h>
#include <pthread.h>
#include <signal.h>

#define MAX_URI_LENGTH (30)
static char a_light[MAX_URI_LENGTH];
static oc_endpoint_t *light_server;

static switch_state my_state = { .state = false, .discovered = false,
  .error_state = false, .error_message = NULL};

static int
app_init(void)
{
  int ret = oc_init_platform("Raspberry Pi", NULL, NULL);
  ret |= oc_add_device("/oic/d", "oic.d.switch", "SO Light Switch", "ocf.1.0.0",
                       "ocf.res.1.0.0", NULL, NULL);
  return ret;
}

static void
post_light_response_cb(oc_client_response_t *data)
{
  if (data->code > OC_STATUS_CHANGED) {
    OC_ERR("POST returned unexpected response code %d\n", data->code);
    my_state.error_state = true;
    my_state.error_message = "POST to light returned unexpected response";
  }
  else {
    my_state.state = !my_state.state;
  }
  external_cb(&my_state);
  my_state.error_state = false;
}

void
toggle_light(void)
{
  if (!my_state.discovered) {
    return;
  }
  if (oc_init_post(a_light, light_server, NULL, &post_light_response_cb, LOW_QOS, NULL)) {
    oc_rep_start_root_object();
    oc_rep_set_boolean(root, state, !my_state.state);
    oc_rep_end_root_object();
    if (oc_do_post()) {
      OC_DBG("Sent POST request\n");
    }
    else {
      OC_ERR("Could not send POST request\n");
    }
  } else {
    OC_ERR("Could not init POST request\n");
  }
}

static void
get_light(oc_client_response_t *data)
{
  if (data->code != OC_STATUS_OK) {
    my_state.error_state = true;
    my_state.error_message = "GET failed with unexpected response";
  }
  oc_rep_t *rep = data->payload;
  while (rep != NULL) {
    switch (rep->type) {
    case OC_REP_BOOL:
      my_state.state = rep->value.boolean;
      break;
    default:
      break;
    }
    rep = rep->next;
  }
  external_cb(&my_state);
  my_state.error_state = false;
}


static oc_discovery_flags_t
discovery_cb(const char *anchor, const char *uri, oc_string_array_t types,
    oc_interface_mask_t iface_mask, oc_endpoint_t *endpoint,
    oc_resource_properties_t bm, void *user_data)
{
  (void)anchor;
  (void)iface_mask;
  (void)bm;
  (void)user_data;
  int i;
  int uri_len = strlen(uri);
  uri_len = (uri_len >= MAX_URI_LENGTH) ? MAX_URI_LENGTH - 1 : uri_len;
  for (i = 0; i < (int)oc_string_array_get_allocated_size(types); i++) {
    char *t = oc_string_array_get_item(types, i);
    if (strlen(t) == 10 && strncmp(t, "core.light", 10) == 0) {
      oc_endpoint_list_copy(&light_server, endpoint);
      strncpy(a_light, uri, uri_len);
      a_light[uri_len] = '\0';

      OC_DBG("Resource %s discovered\n", a_light);
      my_state.discovered = true;
      oc_do_get(a_light, light_server, NULL, &get_light, LOW_QOS, NULL);
      return OC_STOP_DISCOVERY;
    }
  }
  return OC_CONTINUE_DISCOVERY;
}

void
discover_light(void)
{
  oc_do_ip_discovery("core.light", &discovery_cb, NULL);
}

static void
issue_requests(void)
{
  discover_light();
}

int
so_switch_init(char *storage_path, char *so_ctrl_iface, void (*cb)(switch_state *state))
{
  int init;
  struct sigaction sa;
  sigfillset(&sa.sa_mask);
  sa.sa_flags = 0;
  sa.sa_handler = handle_signal;
  sigaction(SIGINT, &sa, NULL);

  static const oc_handler_t handler = { .init = app_init,
    .signal_event_loop = signal_event_loop,
    .requests_entry = issue_requests,
    .register_resources = NULL };

  OC_DBG("Calling storage config with path %s\n", storage_path);
  oc_storage_config(storage_path);
  init = oc_main_init(&handler);
  if (init < 0)
    return init;

  set_external_cb(cb);

  if (oc_so_info_init() == 0) {
    OC_DBG("Generated streamlined onboarding info");
    if (dpp_so_init(so_ctrl_iface) < 0 || dpp_send_so_info() < 0) {
      OC_ERR("Failed to provide streamlined onboarding information to wpa_supplicant");
    }
  }
  return 0;
}

