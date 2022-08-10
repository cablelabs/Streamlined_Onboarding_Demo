#include "socommon.h"
#include "oc_api.h"
#include "port/oc_clock.h"
#include "ocf_dpp.h"
#include <stdio.h>
#include <pthread.h>
#include <signal.h>

int quit = 0;
pthread_mutex_t mutex;
pthread_cond_t cv;
struct timespec ts;

external_cb_t external_cb = NULL;

void
set_external_cb(external_cb_t new_cb)
{
  external_cb = new_cb;
}

void
signal_event_loop(void)
{
  pthread_mutex_lock(&mutex);
  pthread_cond_signal(&cv);
  pthread_mutex_unlock(&mutex);
}

void
handle_signal(int signal)
{
  (void)signal;
  OC_DBG("handle signal called\n");
  quit = 1;
  signal_event_loop();
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
