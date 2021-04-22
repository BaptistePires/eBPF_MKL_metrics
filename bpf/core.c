#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

#define SEC(NAME) __attribute__((section(NAME), used))

int core(void *ctx) {
  
  bpf_printk("Hello world :)\n");
  return 0;
}

