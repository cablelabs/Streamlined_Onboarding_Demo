#ifndef SOLAMP_H
#define SOLAMP_H
#include "socommon.h"

int so_lamp_set_state(bool state);
int so_lamp_init(char *storage_path, char *so_config_path,
                   void (*cb)(switch_state *state));

#endif
