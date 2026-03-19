# Python-C 混合引擎 Makefile

CC = gcc
CFLAGS = -Wall -Wextra -fPIC -g -O2
LDFLAGS = -shared
LDLIBS = -lpython3.11

# IBus 路径
IBUS_PATH = /usr/include/ibus
IBUS_LIB = /usr/lib/x86_64-linux-gnu/libibus-1.0.so.1

# Python 路径
PYTHON_INC = $(shell python3-config --includes)
PYTHON_LIB = $(shell python3-config --ldflags)

# 源文件
SRCDIR = src
SRC_FILES = $(SRCDIR)/my-input-engine.c \
            $(SRCDIR)/ibus-input-engine.c \
            $(SRCDIR)/ibus-input-engine-desc.c

# 目标文件
TARGET = plugin.so

# 默认目标
all: $(TARGET)

$(TARGET): $(SRC_FILES)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(SRC_FILES) \
		-I$(IBUS_PATH) \
		$(PYTHON_INC) \
		$(PYTHON_LIB) \
		-L$(IBUS_LIB) -lbus-1.0 \
		-Wl,-rpath,/usr/lib/x86_64-linux-gnu

clean:
	rm -f $(TARGET)

install: $(TARGET)
	install -m 644 $(TARGET) /usr/lib/ibus/ibus-engines/

uninstall:
	rm -f /usr/lib/ibus/ibus-engines/plugin.so

.PHONY: all clean install uninstall
