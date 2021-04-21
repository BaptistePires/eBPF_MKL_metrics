#include <linux/bpf.h>
#include <linux/types.h>
#include <bpf/bpf_helpers.h>

#define SEC(NAME) __attribute__((section(NAME), used))

// static int (*bpf_trace_printk)(const char *fmt, int fmt_size,
//                                ...) = (void *)BPF_FUNC_trace_printk;

struct bpf_map_def SEC("maps") read_count = {
	.type        = BPF_MAP_TYPE_ARRAY,
	.key_size    = sizeof(int), /* class; u32 required */
	.value_size  = sizeof(int), /* count of mads read */
	.max_entries = 100, /* Room for all Classes */
};


SEC("tracepoint/printk/console")
int bpf_prog(void *ctx) {
  
  char msg[] = "Hello, BPF World!";
  bpf_trace_printk(msg, sizeof(msg));
  int key = 1;
  int value = 1234;
  int result = bpf_map_update_elem(&read_count, &key, &value, BPF_ANY);
  bpf_printk("value insterted : %d\n", result);

  return 0;
}

char _license[] SEC("license") = "GPL";

