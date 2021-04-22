#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

#define SEC(NAME) __attribute__((section(NAME), used))

// SEC("tracepoint/printk/console")
int core(void *ctx) {
  
  bpf_printk("Hello world :)\n");
  return 0;
}


// char _license[] SEC("license") = "GPL";