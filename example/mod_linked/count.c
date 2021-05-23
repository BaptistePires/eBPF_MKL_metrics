#include <linux/init.h>
#include <linux/module.h>
#include <linux/types.h>
#include <linux/kernel.h>
#include <linux/moduleparam.h>
#include <linux/tracepoint.h>
#include <linux/kprobes.h>
#include <linux/kobject.h>
#include <linux/random.h>
#include <linux/bpf.h>

MODULE_DESCRIPTION("Module \"hello world param\"");
MODULE_AUTHOR("Leif Henriksen");
MODULE_LICENSE("GPL");

enum TPoints {
	      SYS_ENTER,
	      SYS_EXIT,
	      TPOINT_COUNT
};

static struct tracepoint  *t_points[TPOINT_COUNT];

static char* t_point_names[TPOINT_COUNT] = {
	"sys_enter",
	"sys_exit",
};

static void lookup_tps(struct tracepoint *tp, void *priv) {
	int i = 0;
	for(; i < TPOINT_COUNT; i++)
	{
		if(strcmp(tp->name, t_point_names[i]) == 0){
		        printk("found %s\n", t_point_names[i]);
			t_points[i] = tp;
		}
	}	
}

extern struct kobject *kernel_kobj;

struct store_time {
    __u64 times[100];
    __u8 count;
} static time_values;

static ssize_t helloWorld_show(struct kobject *kobj, 
								struct kobj_attribute *attr, char *buf)
{
	ssize_t idx = 0, i;
	for(i = 0; i < time_values.count; ++i){
		if(i == time_values.count - 1)
			idx += sprintf(&buf[idx], "%llu", time_values.times[i]);
		else
			idx += sprintf(&buf[idx], "%llu,", time_values.times[i]);
	}

	return idx;
}

static struct kobj_attribute helloWorld_attr = __ATTR_RO(helloWorld);

#define MAP_SIZE 2500

static __u64 linked_list_map[MAP_SIZE];

__attribute__((optimize("unroll-loops")))
static  void test(void)
{
  __u64 t0, delta;
  u32 i, j, res;
  __u64 now;
  __u64 sum = 0;
  t0 = ktime_get_mono_fast_ns();

	for(i = 0; i < MAP_SIZE; i++)
	{
	now = ktime_get_mono_fast_ns();
	linked_list_map[i] = now;
	}

	for(i = 0; i < MAP_SIZE; i++)
	{
		j = get_random_u32();
	//       get_random_bytes(&j, sizeof(j));
	j = j % MAP_SIZE;
	sum += linked_list_map[j];
	}
  
  delta = ktime_get_mono_fast_ns() - t0;

  //printk("Fin test() : ttc = %llu\n", delta);
  
  if(time_values.count < 100){
    time_values.times[time_values.count++] = delta;
  }
}

static void probe_enter(struct pt_regs *regs, long syscall)
{
  if(((struct pt_regs*)syscall)->orig_ax == 6 || ((struct pt_regs*)syscall)->orig_ax == 257)
    {
      test();
    }
}

static void probe_exit(struct pt_regs *regs, long syscall)
{
    if(((struct pt_regs*)syscall)->orig_ax == 6 || ((struct pt_regs*)syscall)->orig_ax == 257)
    {
      test();
    }
}

static int __init count_init(void)
{
        int ret;
	int i = 0;
	printk("count : init\n");

	for_each_kernel_tracepoint(lookup_tps, NULL);
	for(; i < TPOINT_COUNT; i++)
	{
		if(t_points[i] == NULL)
		{
			printk("count : Error: %s not found\n", t_point_names[i]);
			return -1;
		}
	}
	i = 0;
	i += tracepoint_probe_register(t_points[0], probe_enter, NULL);
	i += tracepoint_probe_register(t_points[1], probe_exit, NULL);
	if(i) {
		printk(KERN_INFO "regist fail.\n");
		return -1;
	}

	ret = sysfs_create_file(kernel_kobj, &helloWorld_attr.attr);
	if(ret){
        	pr_warn("Error while creating sysfs fils helloWorld\n");
		return -1;
	}
	
	return 0;
}
module_init(count_init);

static void __exit count_exit(void)
{
        sysfs_remove_file(kernel_kobj, &helloWorld_attr.attr);
	tracepoint_probe_unregister(t_points[0], probe_enter, NULL);
	tracepoint_probe_unregister(t_points[1], probe_exit, NULL);
	printk("count : exit\n");
}
module_exit(count_exit);

