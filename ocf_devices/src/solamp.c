#include "oc_api.h"
#include "port/oc_clock.h"
#include "ocf_dpp.h"
#include "solamp.h"
#include "socommon.h"
#include <stdio.h>
#include <pthread.h>
#include <signal.h>

static switch_state my_state = { .state = false, .discovered = false,
  .error_state = false, .error_message = NULL};

void
set_state(bool state)
{
  my_state.state = state;
}

static int
app_init(void)
{
  int ret = oc_init_platform("Raspberry Pi", NULL, NULL);
  ret |= oc_add_device("/oic/d", "oic.d.light", "SO Lamp", "ocf.1.0.0",
                       "ocf.res.1.0.0", NULL, NULL);
  return ret;
}

static void
post_light(oc_request_t *request, oc_interface_mask_t iface_mask, void *user_data)
{
  (void)iface_mask;
  (void)user_data;
  OC_DBG("POST_light:\n");
  oc_rep_t *rep = request->request_payload;
  while (rep != NULL) {
    OC_DBG("key: %s ", oc_string(rep->name));
    switch (rep->type) {
    case OC_REP_BOOL:
      my_state.state = rep->value.boolean;
      OC_DBG("value: %d\n", state);
      break;
    default:
      oc_send_response(request, OC_STATUS_BAD_REQUEST);
      my_state.error_state = true;
      my_state.error_message = "POST to light was a bad request";
      return;
      break;
    }
    rep = rep->next;
  }
  oc_send_response(request, OC_STATUS_CHANGED);
  external_cb(&my_state);
  my_state.error_state = false;
}

static void
get_light(oc_request_t *request, oc_interface_mask_t iface_mask, void *user_data)
{
  (void)user_data;

  PRINT("GET_light:\n");
  oc_rep_start_root_object();
  switch (iface_mask) {
  case OC_IF_BASELINE:
    oc_process_baseline_interface(request->resource);
  /* fall through */
  case OC_IF_RW:
    oc_rep_set_boolean(root, state, my_state.state);
    break;
  default:
    break;
  }
  oc_rep_end_root_object();
  oc_send_response(request, OC_STATUS_OK);
}

static void
register_resources(void)
{
  oc_resource_t *res = oc_new_resource(NULL, "/a/light", 1, 0);
  oc_resource_bind_resource_type(res, "core.light");
  oc_resource_bind_resource_interface(res, OC_IF_RW);
  oc_resource_set_default_interface(res, OC_IF_RW);
  oc_resource_set_discoverable(res, true);
  oc_resource_set_request_handler(res, OC_GET, get_light, NULL);
  oc_resource_set_request_handler(res, OC_POST, post_light, NULL);
  oc_add_resource(res);
}

int
so_lamp_init(char *storage_path, char *so_ctrl_iface, void (*cb)(switch_state *state))
{
  int init;
  struct sigaction sa;
  sigfillset(&sa.sa_mask);
  sa.sa_flags = 0;
  sa.sa_handler = handle_signal;
  sigaction(SIGINT, &sa, NULL);

  static const oc_handler_t handler = { .init = app_init,
    .signal_event_loop = signal_event_loop,
    .register_resources = register_resources };

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

