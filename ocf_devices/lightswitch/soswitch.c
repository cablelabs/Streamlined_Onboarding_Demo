#include "oc_api.h"
#include "port/oc_clock.h"
#include "ocf_dpp.h"
#include "soswitch.h"
#include <stdio.h>
#include <pthread.h>
#include <signal.h>

#define MAX_URI_LENGTH (30)
static char a_light[MAX_URI_LENGTH];
static oc_endpoint_t *light_server;

static switch_state my_state = { .state = false, .discovered = false };

static int quit = 0;
static pthread_mutex_t mutex;
static pthread_cond_t cv;
static struct timespec ts;

external_cb_t external_cb = NULL;

void
set_external_cb(external_cb_t new_cb)
{
  external_cb = new_cb;
}

static int
app_init(void)
{
  int ret = oc_init_platform("Raspberry Pi", NULL, NULL);
  ret |= oc_add_device("/oic/d", "oic.d.switch", "SO Light Switch", "ocf.1.0.0",
                       "ocf.res.1.0.0", NULL, NULL);
  return ret;
}

static void
signal_event_loop(void)
{
  pthread_mutex_lock(&mutex);
  pthread_cond_signal(&cv);
  pthread_mutex_unlock(&mutex);
}

static void
post_light_response_cb(oc_client_response_t *data)
{
  if (data->code > OC_STATUS_CHANGED) {
    OC_ERR("POST returned unexpected response code %d\n", data->code);
  }
  else {
    my_state.state = !my_state.state;
  }
  external_cb(&my_state);
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
    if (oc_do_post())
      PRINT("Sent POST request\n");
    else
      PRINT("Could not send POST request\n");
  } else
    PRINT("Could not init POST request\n");
}

static void
get_light(oc_client_response_t *data)
{
  oc_rep_t *rep = data->payload;
  while (rep != NULL) {
    switch (rep->type) {
    case OC_REP_BOOL:
      PRINT("%d\n", rep->value.boolean);
      my_state.state = rep->value.boolean;
      break;
    default:
      break;
    }
    rep = rep->next;
  }
  external_cb(&my_state);
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

      PRINT("Resource %s hosted at endpoints:\n", a_light);
      oc_endpoint_t *ep = endpoint;
      while (ep != NULL) {
        PRINTipaddr(*ep);
        PRINT("\n");
        ep = ep->next;
      }
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

void
handle_signal(int signal)
{
  (void)signal;
  printf("handle signal called\n");
  signal_event_loop();
  quit = 1;
}

int
so_switch_init(char *storage_path, char *so_config_path, void (*cb)(switch_state *state))
{
  int init;
  struct sigaction sa;
  sigfillset(&sa.sa_mask);
  sa.sa_flags = 0;
  sa.sa_handler = handle_signal;
  sigaction(SIGINT, &sa, NULL);

  static const oc_handler_t handler = { .init = app_init,
    .signal_event_loop = signal_event_loop,
    .requests_entry = issue_requests };

  printf("Calling storage config with path %s\n", storage_path);
  oc_storage_config(storage_path);
  init = oc_main_init(&handler);
  if (init < 0)
    return init;

  set_external_cb(cb);

  if (oc_so_info_init() == 0) {
    OC_DBG("Generated streamlined onboarding info");
    if (dpp_so_init(so_config_path) < 0 || dpp_send_so_info() < 0) {
      OC_ERR("Failed to provide streamlined onboarding information to wpa_supplicant");
    }
  }
  return 0;
}

int
so_switch_main_loop(void)
{
  oc_clock_time_t next_event;
  while (quit != 1) {
    next_event = oc_main_poll();
    pthread_mutex_lock(&mutex);
    if (next_event == 0) {
      pthread_cond_wait(&cv, &mutex);
    } else {
      ts.tv_sec = (next_event / OC_CLOCK_SECOND);
      ts.tv_nsec = (next_event % OC_CLOCK_SECOND) * 1.e09 / OC_CLOCK_SECOND;
      pthread_cond_timedwait(&cv, &mutex, &ts);
    }
    pthread_mutex_unlock(&mutex);
  }
  oc_main_shutdown();
  return 0;
}
