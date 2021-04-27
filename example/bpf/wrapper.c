#include <linux/bpf.h>
#include <linux/types.h>
#include <bpf/bpf_helpers.h>


#define SEC(NAME) __attribute__((section(NAME), used))

#include "core.c"


/**
 * Map used to share data with user space.
 * Key with value 0 stores the total of entries in the map
 * Keys > 0 stores values
 **/
// struct {
//     __uint(type, BPF_MAP_TYPE_ARRAY);
//     __type(key, __u8);
//     __type(value, __u64);
//     __uint(max_entries, 100);
//     __uint(map_flags, BPF_F_NO_PREALLOC);

// } time_map SEC("maps");
struct bpf_map_def SEC("maps") time_map = {
      .type        = BPF_MAP_TYPE_ARRAY,
      .key_size    = sizeof(__u32),
      .value_size  = sizeof(__u64),
      .max_entries = 101,
      .map_flags   = 0
};

void inc_ptr_content(int *ptr);

static __always_inline void update_time(void *map, __u64 *new_value)
{
    __u32 key = 0, *count_keys;
    __u64 next_key;

    // Retrieve current items count
    count_keys = bpf_map_lookup_elem(map, &key);
    if(count_keys && (*count_keys <= 100)){


        // Compute next key and insert it
        next_key = (*count_keys) + 1;

        bpf_map_update_elem(map, &next_key, new_value, BPF_ANY);
        bpf_map_update_elem(map, &key, &next_key, BPF_EXIST);
    }else{
        next_key = 0;
        bpf_map_update_elem(map, &key, &next_key, BPF_NOEXIST);
    }

}

SEC("kprobe/printk")
int bpf_prog(void *ctx) {
    __u64 t0, delta;
    int res;
    t0 = bpf_ktime_get_ns();

    // #pragma unroll
    // for(i = 0; i < 50; ++i)
    //     res += i* nibble;
    bpf_ktime_get_ns();
    // bpf_ktime_get_ns();
    // bpf_ktime_get_ns();
    
    // bpf_printk("Hello World%d\n", res);

    delta = bpf_ktime_get_ns() - t0;

    update_time(&time_map, &delta);

    return res;
}

char _license[] SEC("license") = "GPL"; 