// #include <linux/bpf.h>
// #include <linux/types.h>
// #include <bpf/bpf_helpers.h>


// #define SEC(NAME) __attribute__((section(NAME), used))

// #include "core.c"


// /**
//  * Map used to share data with user space.
//  * Key with value 0 stores the total of entries in the map
//  * Keys > 0 stores values
//  **/
// // struct {
// //     __uint(type, BPF_MAP_TYPE_ARRAY);
// //     __type(key, __u8);
// //     __type(value, __u64);
// //     __uint(max_entries, 100);
// //     __uint(map_flags, BPF_F_NO_PREALLOC);
     
// // } time_map SEC("maps");
// struct bpf_map_def SEC("maps") time_map = {
//       .type        = BPF_MAP_TYPE_ARRAY,
//       .key_size    = sizeof(__u32),
//       .value_size  = sizeof(__u64),
//       .max_entries = 101,
//       .map_flags   = 0
// };

// void inc_ptr_content(int *ptr);

// static __always_inline void update_time(void *map, __u64 *new_value)
// {
//     __u32 key = 0, *count_keys;
//     __u64 next_key;
    
//     // Retrieve current items count
//     count_keys = bpf_map_lookup_elem(map, &key);
//     if(count_keys){

        
//         // Compute next key and insert it
//         next_key = (*count_keys) + 1;

//         bpf_map_update_elem(map, &next_key, new_value, BPF_ANY);
//         bpf_map_update_elem(map, &key, &next_key, BPF_EXIST);
//     }else{
//         next_key = 0;
//         bpf_map_update_elem(map, &key, &next_key, BPF_NOEXIST);
//     }
    
// }

// SEC("tracepoint/printk/console")
// int bpf_prog(void *ctx) {
//     __u64 t0, delta;
//     int res;
    
//     beforeprint:
//     t0 = bpf_ktime_get_ns();
    
//     res = core(ctx);
    
//     delta = bpf_ktime_get_ns() - t0;
    
//     char log[] = "core.c delta = %li\n"; 
//     bpf_trace_printk(log, sizeof(log), delta);
//     // bpf_printk("working at least\n");?
//     update_time(&time_map, &delta);
//     goto loop;
//     label_1:
//     goto beforeprint;

//     int test[1000];

//     int *ptr;

//     loop:
//     #pragma unroll
//     for(ptr = &test[0]; ptr != &test[1000]; ++ptr)
//         // *ptr += str[*ptr % 3];
//         inc_ptr_content(ptr);
        
//     #pragma unroll
//     for(ptr = &test[1000]; ptr != test; ptr--)
//         // *ptr -= str[++(*ptr) % 3];
//         inc_ptr_content(ptr);
//     return res;
// }

// void inc_ptr_content(int *ptr) {
//     char str[3] = "bon";
//     *ptr += *ptr + str[1];
// }


// char _license[] SEC("license") = "GPL";

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

static __always_inline void update_time(void *map, __u64 *new_value)
{
    __u32 key = 0, *count_keys;
    __u64 next_key;
    
    // Retrieve current items count
    count_keys = bpf_map_lookup_elem(map, &key);
    if(count_keys && (*count_keys < 100)){

        // Compute next key and insert it
        next_key = (*count_keys) + 1;

        bpf_map_update_elem(map, &next_key, new_value, BPF_ANY);
        bpf_map_update_elem(map, &key, &next_key, BPF_EXIST);
    }else{
        next_key = 0;
        bpf_map_update_elem(map, &key, &next_key, BPF_NOEXIST);
    }
    
}

SEC("tracepoint/printk/console")
int bpf_prog(void *ctx) {
    __u64 t0, delta;
    int res;
    
    t0 = bpf_ktime_get_ns();
    
    res = core(ctx);
    
    delta = bpf_ktime_get_ns() - t0;
    
    char log[] = "core.c delta = %li\n"; 
    bpf_trace_printk(log, sizeof(log), delta);
    bpf_printk("working at least\n");
    update_time(&time_map, &delta);
    return res;
}

char _license[] SEC("license") = "GPL";