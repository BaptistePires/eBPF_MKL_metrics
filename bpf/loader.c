#include "bpf_load.h"
#include <stdio.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <linux/bpf.h>

#include <signal.h>
#include <error.h>
#include <errno.h>
#define FIFO_PATH "/tmp/fifo"
// .csv tmp
#define SAVE_FILENAME "time_values.csv"

void retrieve_map_value(void);

void handler(int sign){
  return;
}

int fifo_read_fd, fifo_write_fd;
char *fifo_read_path, *fifo_write_path;

int main(int argc, char **argv) {
    
  if(argc < 4){
    printf("Usage %s <bpf_filename> <fifo_read_path> <fifo_write_path>", argv[0]);
  }

  fifo_read_path = argv[2];
  fifo_write_path = argv[3];
  signal(SIGCONT, handler);
  if (load_bpf_file(argv[1]) != 0) {
      printf("The kernel didn't load the BPF program\n");
      perror("bpf");
      return -1;
  }else{

    // mkfifo(fifo_read_path, 0666);
    // mkfifo(fifo_write_path, 0666);
    // fifo_read_fd = open(fifo_read_path, O_RDWR);
    // fifo_write_fd = open(fifo_write_path, O_RDWR);

    // if(fifo_read_fd <= 0 || fifo_write_fd <= 0) {
    //   printf("Error while opening pipes\n");
    //   printf("-1\n");
    //   return -1;
    // }

    // fprintf(fifo_write_fd, "%d\n", 1);
    // fflush(fifo_write_fd);
    
    // dprintf(fifo_write_fd, "%d\n", 1);
    printf("1");
    fflush(stdout);
    retrieve_map_value();
    
    // fprintf(fifo_write_fd, "%d", 1);
    // fclose(fifo_read_fd);
    // fclose(fifo_write_fd);
  }
            
  // retrieve_map_value();

  return 0;
}

void retrieve_map_value(void)
{
  __u64 *time_values;
  __u64 value_count;
  __u64 value;
  __u32 key = 0;
  
  pause();

  if(bpf_map_lookup_elem(map_data[0].fd, &key, &value_count)) {
    perror("bpf_map_lookup_elem");
    printf("-1");
    return ;
  }

  time_values = (__u64 *) malloc(sizeof(__u64) * value_count);
  if(time_values == NULL){
    perror("malloc");
    printf("-1");
    fflush(stdout);
    return;
  }

  __u32 tmp_key = 1;
  for(;tmp_key < (value_count - 1) ; ++tmp_key) {
    if(bpf_map_lookup_elem(map_data[0].fd, &tmp_key, &value)) {
      perror("bpf_map_lookup_elem");
      printf("-1");
      fflush(stdout);
      return ;
    }
    time_values[tmp_key - 1] = value;
  }

  FILE* save_file;
  save_file = fopen(SAVE_FILENAME, "w+");
  if(save_file == NULL) {
    printf("-1");
    goto end;
  }
  ;

  char *fmt = "%llu,";
  for(__u32 i = 0; i < value_count; ++i) {
    if(i == value_count - 1) fmt = "%llu";
    fprintf(save_file, fmt, time_values[i]);
  }
  fclose(save_file);
  
  printf("1");
  
  end:
  free(time_values);
  fflush(stdout);
}