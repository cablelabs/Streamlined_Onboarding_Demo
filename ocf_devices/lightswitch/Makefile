export CC=gcc
CROSS=0
ifeq ($(CROSS), 1)
	export CC=arm-linux-gnueabihf-gcc
endif

LITE_DIR=../../deps/SO_IoTivity-Lite
CLIENT_LIB=$(LITE_DIR)/port/linux/libiotivity-lite-client.a
SERVER_LIB=$(LITE_DIR)/port/linux/libiotivity-lite-server.a
LITE_LIBS=$(CLIENT_LIB) $(SERVER_LIB)
LITE_INCLUDES=-I$(LITE_DIR) $(addprefix -I$(LITE_DIR)/, include port/linux apps/streamlined_onboarding/include)
CFLAGS=-fPIC -fno-asynchronous-unwind-tables -fno-omit-frame-pointer -ffreestanding -Os -fno-stack-protector -ffunction-sections -fdata-sections -fno-reorder-functions -fno-defer-pop -fno-strict-overflow -std=gnu99 -Wall -Wextra -Werror -pedantic
LIBS=-lm -pthread -lrt -lwpa_client
SO_DPP=1

all: lightswitch

$(LITE_LIBS):
	cd $(dir $@) && make CC=$(CC) SO_DPP=1 $(notdir $@)

.PHONY: clean-lite
clean-lite:
	cd $(LITE_DIR)/port/linux && make cleanall

soswitch.o: soswitch.c
	@$(CC) -c -o $@ $^ -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

libsoswitch.so: soswitch.o $(CLIENT_LIB)
	@$(CC) -shared -o $@ $^ -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

lightswitch: lightswitch.c $(CLIENT_LIB)
	@mkdir -p $@_creds
	@$(CC) -o $@ $^ $(CLIENT_LIB) -DOC_CLIENT $(CFLAGS) $(LITE_INCLUDES) $(LIBS)
	@echo $(CC) $@

clean:
	rm -rf lightswitch lightswitch_creds libsoswitch.so soswitch.o
