CC = gcc
CFLAGS = -g -Wall -Wextra -pedantic -std=c99 -Wformat=2 -Wstrict-aliasing=3 -Wfloat-equal -Wundef -Wcast-qual -Wconversion 
INCLUDE = -I/usr/include/SDL -I/usr/local/include/SDL -I/usr/X11R6/include
LDFLAGS = -L/usr/lib -L/usr/local/lib -lSDL -lSDLmain -L/usr/X11R6/lib -lGL -lpthread
SPLINT = splint
SPLINTFLAGS = -predboolint -linelen 10000 -boolops
all:
	${CC} ${CFLAGS} ${INCLUDE} ${LDFLAGS} *.c -o coverband

splint:
	${SPLINT} ${INCLUDE} ${SPLINTFLAGS} *.c

clean:
	-rm *.s *.i *.o
