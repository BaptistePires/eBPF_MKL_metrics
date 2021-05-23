// SPDX-License-Identifier: GPL-2.0-only
/* Copyright (c) 2017 Facebook
 */
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <linux/perf_event.h>
#include <errno.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <signal.h>

#define SAVE_FILENAME "time_values.csv"

/* This program verifies bpf attachment to tracepoint sys_enter_* and sys_exit_*.
 * This requires kernel CONFIG_FTRACE_SYSCALLS to be set.
 */

//  make; mv bpf_program.o monitor-exec_kern.o
//  ./monitor-exec

int fifo_read_fd, fifo_write_fd;
char *fifo_read_path, *fifo_write_path;

void retrieve_map_value(int map_id)
{
        __u64 *time_values;
        __u64 value_count;
        __u64 value;
        __u32 key = 0;

        if (bpf_map_lookup_elem(map_id, &key, &value_count))
        {
                perror("bpf_map_lookup_eleem");
                printf("-1");
                goto end;
        }
        fprintf(stderr, "value count : %llu\n", value_count);
        time_values = (__u64 *)malloc(sizeof(__u64) * value_count);
        if (time_values == NULL)
        {
                perror("malloc");
                printf("-1");
                fflush(stdout);
                goto end;
        }

        __u32 tmp_key = 1;
        for (; tmp_key < (value_count + 1); ++tmp_key)
        {
                if (bpf_map_lookup_elem(map_id, &tmp_key, &value))
                {
                        perror("bpf_map_lookup_eleeeeem");
                        printf("-1");
                        fflush(stdout);
                        goto end;
                }
                time_values[tmp_key - 1] = value;
        }

        FILE *save_file;
        save_file = fopen(SAVE_FILENAME, "w+");
        if (save_file == NULL)
        {
                printf("-1");
                goto end;
        };

        char *fmt = "%llu,";
        for (__u32 i = 0; i < value_count; ++i)
        {
                if (i == value_count - 1)
                        fmt = "%llu";
                fprintf(save_file, fmt, time_values[i]);
        }
        fclose(save_file);

        printf("1");

end:
        free(time_values);
}

static void verify_map(int map_id)
{
        __u32 key = 0;
        __u64 val;

        if (bpf_map_lookup_elem(map_id, &key, &val) != 0)
        {
                fprintf(stderr, "map_lookup failed: %s\n", strerror(errno));
                return;
        }

        printf("verify_map(map_id = %i) result : key = %i, val = %llu\n", map_id, key, val);

        if (bpf_map_update_elem(map_id, &key, &val, BPF_ANY) != 0)
        {
                fprintf(stderr, "map_update failed: %s\n", strerror(errno));
                return;
        }
}

static void print_map(int map_id)
{
        __u32 ttc = 0;
        __u32 res = 1;
        __u64 val1;
        __u64 val2;
        int err = 0;

        err += bpf_map_lookup_elem(map_id, &ttc, &val1);
        err += bpf_map_lookup_elem(map_id, &res, &val2);

        if (err != 0)
        {
                fprintf(stderr, "map_lookup failed: %s\n", strerror(errno));
                return;
        }

        printf("verify_map(map_id = %i) result : ttc = %llu, res = %llu\n", map_id, val1, val2);
}

static int test(char *filename, int num_progs)
{
        int map0_fds[num_progs], fd, i, j = 0;
        struct bpf_link *links[num_progs * 4];
        struct bpf_object *objs[num_progs]; // The bytecode
        struct bpf_program *prog;

        for (i = 0; i < num_progs; i++)
        {
                // Load the bytecode
                objs[i] = bpf_object__open_file(filename, NULL);
                if (libbpf_get_error(objs[i]))
                {
                        fprintf(stderr, "opening BPF object file failed\n");
                        objs[i] = NULL;
                        goto cleanup;
                }

                /* load BPF program */
                if (bpf_object__load(objs[i]))
                {
                        fprintf(stderr, "loading BPF object file failed\n");
                        goto cleanup;
                }

                // Load the maps
                //map0_fds[i] = bpf_object__find_map_fd_by_name(objs[i], "linked_list_map");
                map0_fds[i] = bpf_object__find_map_fd_by_name(objs[i], "time_to_complete");

                // Check the maps
                if (map0_fds[i] < 0)
                {
                        fprintf(stderr, "finding a map in obj file failed\n");
                        goto cleanup;
                }

                // Attach the programs
                bpf_object__for_each_program(prog, objs[i])
                {
                        links[j] = bpf_program__attach(prog);
                        if (libbpf_get_error(links[j]))
                        {
                                fprintf(stderr, "bpf_program__attach failed\n");
                                links[j] = NULL;
                                goto cleanup;
                        }
                        j++;
                }
                // printf("prog #%d: map ids %d\n", i, map0_fds[i]);
        }
        printf("1");
        fflush(stdout);
        pause();
        // Testing

        /* current load_bpf_file has perf_event_open default pid = -1
   * and cpu = 0, which permits attached bpf execution on
   * all cpus for all pid's. bpf program execution ignores
   * cpu affinity.
   */

        /* trigger some "open" operations */
        // fd = open(filename, O_RDONLY);
        // if (fd < 0)
        // {
        //         fprintf(stderr, "open failed: %s\n", strerror(errno));
        //         return 1;
        // }
        // close(fd);

        /* verify the map */
        for (i = 0; i < num_progs; i++)
        {
                //verify_map(map0_fds[i]);
                retrieve_map_value(map0_fds[i]);
        }

        // End
cleanup:
        for (j--; j >= 0; j--)
                bpf_link__destroy(links[j]);

        for (i--; i >= 0; i--)
                bpf_object__close(objs[i]);
        return 0;
}

void handler(int sign)
{
        return;
}

int main(int argc, char **argv)
{
        struct rlimit r = {RLIM_INFINITY, RLIM_INFINITY};
        int opt, num_progs = 1;
        char filename[256];

        //   while ((opt = getopt(argc, argv, "i:h")) != -1) {
        //     switch (opt) {
        //     case 'i':
        //       num_progs = atoi(optarg);
        //       break;
        //     case 'h':
        //     default:
        //       usage(argv[0]);
        //       return 0;
        //     }
        //   }

        setrlimit(RLIMIT_MEMLOCK, &r);
        snprintf(filename, sizeof(filename), "wrapper.o");
        if (argc < 4)
        {
                printf("Usage %s <bpf_filename> <fifo_read_path> <fifo_write_path>", argv[0]);
        }

        fifo_read_path = argv[2];
        fifo_write_path = argv[3];
        signal(SIGCONT, handler);

        if (test(filename, num_progs))
        {
                printf("Error in test\n");
                return 1;
        }
        // test(filename, num_progs);
        return 0;
}