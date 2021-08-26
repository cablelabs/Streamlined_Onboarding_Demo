typedef struct {
  bool state;
  bool discovered;
} switch_state;

typedef void (*external_cb_t)(switch_state *);

void set_external_cb(external_cb_t new_cb);
void discover_light(void);
void toggle_light(void);
void handle_signal(int signal);
int so_switch_init(char *storage_path, char *so_config_path,
                   void (*cb)(switch_state *state));
int so_switch_main_loop(void);
