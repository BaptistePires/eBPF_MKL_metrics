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
#include "bpf_load.h"
#include <stdio.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <linux/bpf.h>

/* This program verifies bpf attachment to tracepoint sys_enter_* and sys_exit_*.
 * This requires kernel CONFIG_FTRACE_SYSCALLS to be set.
 */

//  make; mv bpf_program.o monitor-exec_kern.o
//  ./monitor-exec
#include <signal.h>
#include <error.h>
#include <errno.h>
#define FIFO_PATH "/tmp/fifo"
#define SAVE_FILENAME "time_values.csv"

static void usage(const char *cmd)
{
	printf("USAGE: %s [-i num_progs] [-h]\n", cmd);
	printf("       -i num_progs      # number of progs of the test\n");
	printf("       -h                # help\n");
}
void retrieve_map_value(int map_id)
{
	__u64 *time_values;
	__u64 value_count;
	__u64 value;
	__u32 key = 0;

	pause();

	if (bpf_map_lookup_elem(map_id, &key, &value_count))
	{
		perror("bpf_map_lookup_elem");
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
	for (; tmp_key < (value_count - 1); ++tmp_key)
	{
		if (bpf_map_lookup_elem(map_id, &tmp_key, &value))
		{
			perror("bpf_map_lookup_elem");
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
		// printf("prog #%d: map ids %d\n", i, map0_fds[i]);s
	}

	// Testing

	/* current load_bpf_file has perf_event_open default pid = -1
   * and cpu = 0, which permits attached bpf execution on
   * all cpus for all pid's. bpf program execution ignores
   * cpu affinity.
   */
	/* verify the map */
	for (i = 0; i < num_progs; i++)
	{
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


int fifo_read_fd, fifo_write_fd;
char *fifo_read_path, *fifo_write_path;

int main(int argc, char **argv)
{
	struct rlimit r = {RLIM_INFINITY, RLIM_INFINITY};
	int opt, num_progs = 1;
	char filename[256];

	// test(filename, num_progs);
	if (argc < 4)
	{
		printf("Usage %s <bpf_filename> <fifo_read_path> <fifo_write_path>", argv[0]);
	}

	fifo_read_path = argv[2];
	fifo_write_path = argv[3];
	signal(SIGCONT, handler);
	// if (load_bpf_file(argv[1]) != 0)
	// {
	// 	printf("The kernel didn't load the BPF program\n");
	// 	perror("bpf");
	// 	return -1;
	// }
	// else
	// {
		printf("1");
		fflush(stdout);
		test(argv[1], 1);
	// }
	return 0;
}
