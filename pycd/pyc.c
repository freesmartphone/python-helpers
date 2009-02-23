#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SOCKET_PATH "/var/run/pyc_socket"

void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    int i, s, bufsize, bufpos, argsize, pid;
    struct sockaddr_un sa;
    ssize_t len;
    if ((s = socket(AF_UNIX, SOCK_SEQPACKET, 0)) < 0) {
        error("ERROR: could not create socket");
    }
    memset(&sa, 0, sizeof(struct sockaddr_un));
    sa.sun_family = AF_UNIX;
    strncpy(sa.sun_path, SOCKET_PATH, sizeof(sa.sun_path) - 1);
    if (connect(s, (struct sockaddr *) &sa, sizeof(sa)) < 0 ) {
        error("ERROR: could not connect");
    }

    bufsize = 0;
    for (i = 1; i < argc; i++) {
        bufsize += 4 + strlen(argv[i]);
    }
    char *buffer = malloc( bufsize + 4 );
    memcpy(&buffer[0], &bufsize, sizeof(bufsize));
    bufsize += 4;

    bufpos = 4;
    for (i = 1; i < argc; i++) {
        argsize = strlen(argv[i]);
        memcpy(&buffer[bufpos], &argsize, sizeof(argsize));
        memcpy(&buffer[bufpos+4], argv[i], argsize);
        bufpos += 4 + argsize;
    }

    if ((len = send(s, buffer, bufsize, 0)) < 0) {
        error("ERROR: could not send");
    }

    if ((len = recv(s, &pid, sizeof(pid), 0)) < 0) {
        error("ERROR: could not recv");
    }

    if (len != sizeof(pid)) {
        fprintf(stderr, "ERROR: invalid reply");
    }

    if (waitpid(pid, NULL, 0) < 0) {
        error("ERROR: could not wait for child");
    }

    return 0;
}

