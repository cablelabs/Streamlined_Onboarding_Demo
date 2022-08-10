export CC=gcc
CROSS=0
ifeq ($(CROSS), 1)
	export CC=arm-linux-gnueabihf-gcc
endif

# Lite specific
LITE_DIR=../deps/SO_IoTivity-Lite
CLIENT_LIB=$(LITE_DIR)/port/linux/libiotivity-lite-client.a
SERVER_LIB=$(LITE_DIR)/port/linux/libiotivity-lite-server.a
LITE_LIBS=$(CLIENT_LIB) $(SERVER_LIB)
LITE_INCLUDES=-Iinclude -I$(LITE_DIR) $(addprefix -I$(LITE_DIR)/, include port/linux apps/streamlined_onboarding/include)
CFLAGS=-fPIC -fno-asynchronous-unwind-tables -fno-omit-frame-pointer -ffreestanding -Os -fno-stack-protector -ffunction-sections -fdata-sections -fno-reorder-functions -fno-defer-pop -fno-strict-overflow -std=gnu99 -Wall -Wextra -Werror -Wfatal-errors -pedantic
LIBS=-lm -pthread -lrt -lwpa_client
SO_DPP=1

# Python build items
BUILD_DIRS=build dist so_lightswitch.egg-info

all: slined_onboarding/resources/libso.so

.PHONY: dist
dist: slined_onboarding/resources/libso.so
	python -m build

$(LITE_LIBS):
	cd $(dir $@) && make CC=$(CC) SO_DPP=1 $(notdir $@)

obj:
	@mkdir obj

obj/socommon.o: src/socommon.c obj
	@$(CC) -c -o $@ $< -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

obj/soswitch.o: src/soswitch.c obj
	@$(CC) -c -o $@ $< -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

slined_onboarding/resources/libso.so: obj/soswitch.o obj/socommon.o $(CLIENT_LIB)
	@$(CC) -shared -o $@ $^ -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

lightswitch: slined_onboarding/lightswitch/lightswitch.c $(CLIENT_LIB)
	@mkdir -p $@_creds
	@$(CC) -o $@ $^ $(CLIENT_LIB) -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

clean:
	rm -rf lightswitch lightswitch_creds obj/soswitch.o slined_onboarding/resources/libso.so obj
	rm -rf $(BUILD_DIRS)

.PHONY: clean-lite
clean-lite:
	cd $(LITE_DIR)/port/linux && make cleanall
