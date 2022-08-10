#ifndef SOCOMMON_H
#define SOCOMMON_H
#include <stdbool.h>
#include <pthread.h>

typedef struct {
  bool state;
  bool discovered;
  bool error_state;
  char *error_message;
} switch_state;

typedef void (*external_cb_t)(switch_state *);

extern int quit;
extern pthread_mutex_t mutex;
extern pthread_cond_t cv;
extern struct timespec ts;
extern external_cb_t external_cb;

void signal_event_loop(void);
void set_external_cb(external_cb_t new_cb);
int so_main_loop(void);
#endif
