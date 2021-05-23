#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

#define SEC(NAME) __attribute__((section(NAME), used))

int core(void *ctx) {
  
  __u32 i;
  __u64 res;

  #pragma unroll
  for(i = 0; i < 1000; ++i)
    res += i* 7 + *((int*)ctx) ;

  bpf_printk("salu\n");
  return res;
}

