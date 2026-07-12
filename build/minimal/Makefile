CC ?= m68k-amigaos-gcc
CFLAGS ?= -O2 -Wall -Wextra -Iinclude
TARGET ?= minimal

SOURCES := src/main.c src/generated_project.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $(SOURCES)

clean:
	rm -f $(TARGET)
