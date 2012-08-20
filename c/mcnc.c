/**
 * mcnc - MultiCast-aware NetCat like tool.
 * Author: Tom Wambold <tom5760@gmail.com>
 *
 * Binds to a particular network address/port, and sends anything received on
 * stdin to the specified address/port.  Prints anything received to stdout.
 *
 * Currently only supports sending strings over UDP.  Each null-terminated
 * string is sent its own packet.
 */

#include <errno.h>
#include <poll.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>

/* Logging macros */
#ifdef NDEBUG
#define DEBUG(M, ...)
#else
#define DEBUG(M, ...) fprintf(stderr, "DEBUG %s:%d: " M "\n", __FILE__, __LINE__, ##__VA_ARGS__)
#endif

/* Returns errno as a string if its set. */
#define CLEAN_ERRNO() (errno == 0 ? "None" : strerror(errno))

/* Writes an error message to stderr. */
#define LOG_ERR(M, ...) fprintf(stderr, "[ERROR] (%s:%d: errno: %s) " M "\n", __FILE__, __LINE__, CLEAN_ERRNO(), ##__VA_ARGS__)

/** Writes an information message to stderr. */
#define LOG_INFO(M, ...) fprintf(stderr, "[INFO] (%s:%d) " M "\n", __FILE__, __LINE__, ##__VA_ARGS__)

/* Constants */

static const int DEFAULT_TTL = 64;
static const size_t DEFAULT_RECV_BUFFER_SIZE = 10240;
static const size_t DEFAULT_SEND_BUFFER_SIZE = 102400;

struct send_buffer {
    size_t length;
    size_t offset;
    char buffer[];
};

/* Forward declarations */
static int init_socket(struct in_addr bind_addr, uint16_t bind_port);

static ssize_t read_socket(int fd, char *buffer, size_t len);
static bool read_stdin(const struct sockaddr_in *sa, int fd,
                       struct send_buffer *send_buffer);

static struct send_buffer* new_send_buffer(size_t size);

static bool read_int(const char *arg, long int *output);
static bool read_port(const char *arg, uint16_t *port);
static void print_usage(void);

static int init_socket(struct in_addr bind_addr, uint16_t bind_port) {
    int fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (fd < 0) {
        LOG_ERR("Error creating socket");
        return false;
    }

    int flag;

    flag = 0;
    if (setsockopt(fd, IPPROTO_IP, IP_MULTICAST_LOOP, &flag,
                   sizeof(flag)) != 0) {
        LOG_ERR("Failed setting multicast loop flag");
        goto error;
    }

    flag = DEFAULT_TTL;
    if (setsockopt(fd, IPPROTO_IP, IP_MULTICAST_TTL, &flag,
                   sizeof(flag)) != 0) {
        LOG_ERR("Failed setting multicast ttl flag");
        goto error;
    }

    flag = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag)) != 0) {
        LOG_ERR("Failed making socket address reusable");
        goto error;
    }

    struct sockaddr_in bind_sa = {
        .sin_family = AF_INET,
        .sin_port = htons(bind_port),
        .sin_addr.s_addr = htonl(INADDR_ANY),
    };
    if (bind(fd, (struct sockaddr*)&bind_sa, sizeof(bind_sa)) != 0) {
        LOG_ERR("Failed to bind socket");
        goto error;
    }

    struct ip_mreq req = {
        .imr_multiaddr = bind_addr,
        .imr_interface.s_addr = htonl(INADDR_ANY),
    };
    if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &req,
                   sizeof(req)) != 0) {
        LOG_ERR("Failed to join multicast group");
        goto error;
    }

    return fd;

error:
    if (shutdown(fd, SHUT_RDWR) != 0) {
        LOG_ERR("Failed shutting down socket");
    }
    if (close(fd) != 0) {
        LOG_ERR("Failed closing socket");
    }
    return -1;
}

static ssize_t read_socket(int fd, char *buffer, size_t len) {
    struct sockaddr_in recv_addr;
    socklen_t recv_addr_len = sizeof(recv_addr);

    ssize_t num_recv = recvfrom(fd, buffer, len, 0,
                                (struct sockaddr*)&recv_addr, &recv_addr_len);
    if (num_recv < 0) {
        LOG_ERR("Failed to receive from socket");
    }
    if (num_recv <= 0) {
        return num_recv;
    }

    LOG_INFO("Received %zd bytes from %s:%d", (size_t)num_recv,
             inet_ntoa(recv_addr.sin_addr), ntohs(recv_addr.sin_port));
    printf("%.*s", (int)num_recv, buffer);

    return num_recv;
}

static bool read_stdin(const struct sockaddr_in *sa, int fd,
                       struct send_buffer *send_buffer) {

    ssize_t num_recv = read(0, send_buffer->buffer + send_buffer->offset,
                            send_buffer->length - send_buffer->offset);
    if (num_recv < 0) {
        LOG_ERR("Failed to read from stdin");
    }
    if (num_recv <= 0) {
        return false;
    }
    send_buffer->offset += num_recv;

    char *nullterm;
    do {
        nullterm = memchr(send_buffer->buffer, 0, send_buffer->offset);
        if (nullterm == NULL) {
            break;
        }

        size_t num_sent = sendto(fd, send_buffer->buffer,
                                 nullterm - send_buffer->buffer + 1, 0,
                                 (struct sockaddr*)sa, sizeof(*sa));
        if (num_sent <= 0) {
            LOG_ERR("Failed to send to socket");
            return true;
        }
        LOG_INFO("Sent %zd bytes to socket", (size_t)num_sent);

        memmove(send_buffer->buffer, send_buffer->buffer + num_sent, num_sent);
        send_buffer->offset -= num_sent;
    } while (send_buffer->offset > 0);
    return true;
}

static struct send_buffer* new_send_buffer(size_t size) {
    struct send_buffer *buffer;
    size_t length = sizeof(*buffer) + size;

    buffer = malloc(length);
    if (buffer == NULL) {
        LOG_ERR("Failed to allocate send buffer");
        return NULL;
    }

    buffer->length = length;
    buffer->offset = 0;
    return buffer;
}

static bool read_int(const char *arg, long int *output) {
    /* Clear errno so we can check if strtol fails. */
    errno = 0;

    char *endptr;
    *output = strtol(arg, &endptr, 10);

    /* We want to make sure we read the whole string. */
    return (errno != ERANGE) && (*endptr == '\0');
}

static bool read_port(const char *arg, uint16_t *port) {
    long int out;
    if (!read_int(arg, &out)) {
        return false;
    }

    /* Check that port number is within bounds. */
    if (out > 65535 || out < 0) {
        return false;
    }

    *port = out;
    return true;
}

static void print_usage(void) {
    printf("./mcnc <BIND_ADDR> <BIND_PORT> <SEND_ADDR> <SEND_PORT>\n");
}

int main(int argc, char **argv) {
    if (argc != 5) {
        print_usage();
        return 1;
    }

    struct in_addr bind_addr;
    if (inet_aton(argv[1], &bind_addr) == 0) {
        LOG_ERR("Invalid bind address '%s'", argv[1]);
        return 1;
    }

    uint16_t bind_port;
    if (!read_port(argv[2], &bind_port)) {
        LOG_ERR("Invalid bind port '%s'", argv[2]);
        return 1;
    }

    struct in_addr send_addr;
    if (inet_aton(argv[3], &send_addr) == 0) {
        LOG_ERR("Invalid send address '%s'", argv[3]);
        return 1;
    }

    uint16_t send_port;
    if (!read_port(argv[4], &send_port)) {
        LOG_ERR("Invalid send port '%s'", argv[4]);
        return 1;
    }

    int fd = init_socket(bind_addr, bind_port);
    if (fd < 0) {
        return 1;
    }

    struct sockaddr_in send_sa = {
        .sin_family = AF_INET,
        .sin_addr = send_addr,
        .sin_port = htons(send_port),
    };

    struct pollfd poll_fds[] = {
        {
            .fd = 0,
            .events = POLLIN,
        }, {
            .fd = fd,
            .events = POLLIN,
        },
    };

    struct send_buffer *send_buffer = new_send_buffer(DEFAULT_SEND_BUFFER_SIZE);
    if (send_buffer == NULL) {
        return 1;
    }

    char recv_buffer[DEFAULT_RECV_BUFFER_SIZE];

    while (true) {
        int res = poll(poll_fds, 2, -1);

        if (res == 0) {
            DEBUG("Empty poll output?");
            continue;
        }

        if (res < 0) {
            LOG_ERR("Poll failed");
            return 1;
        }

        if (poll_fds[0].revents & POLLIN
                && !read_stdin(&send_sa, fd, send_buffer)) {
            break;
        }

        if (poll_fds[1].revents & POLLIN
                && read_socket(fd, recv_buffer,
                               DEFAULT_RECV_BUFFER_SIZE) <= 0) {
            break;
        }
    }

    free(send_buffer);

    return 0;
}
