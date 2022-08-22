#ifndef SOSWITCH_H
#define SOSWITCH_H
#include "socommon.h"

void discover_light(void);
void toggle_light(void);
void handle_signal(int signal);
int so_switch_init(char *storage_path, char *so_config_path,
                   void (*cb)(switch_state *state));
#endif
