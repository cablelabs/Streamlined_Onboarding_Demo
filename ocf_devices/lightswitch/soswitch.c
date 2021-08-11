#include "oc_api.h"
#include "port/oc_clock.h"
#include <stdio.h>
#include <pthread.h>
#include <signal.h>

#define MAX_URI_LENGTH (30)
static char a_light[MAX_URI_LENGTH];
static oc_endpoint_t *light_server;

static int quit = 0;
static pthread_mutex_t mutex;
static pthread_cond_t cv;
static struct timespec ts;

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

static oc_discovery_flags_t
discovery_cb(const char *anchor, const char *uri, oc_string_array_t types,
    oc_interface_mask_t iface_mask, oc_endpoint_t *endpoint,
    oc_resource_properties_t bm, void *user_data)
{
  (void)anchor;
  (void)user_data;
  (void)iface_mask;
  (void)bm;
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
so_switch_init(char *storage_path)
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
