#include "bpf_load.h"
#include <linux/bpf.h>

int main(int argc, char **argv) {
  
  if (load_bpf_file(argv[1]) != 0) 
      return -1;
  
  printf("Loader_1\n");
  return 0;
}
