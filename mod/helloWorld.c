#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
#include <linux/kobject.h>
/**
 * Simple module that triggers at each printk calls.
 * Source : https://github.com/spotify/linux/blob/master/samples/kprobes/kprobe_example.c
 **/


extern struct kobject *kernel_kobj;

struct store_time {
    __u64 times[100];
    __u8 count;
}static time_values;

// Target (symbol)
static struct kprobe kp = {
	.symbol_name	= "printk",
};

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

static int handler_pre(struct kprobe *p, struct pt_regs *regs)
{
    __u64 t0, delta;
    t0 = ktime_get_mono_fast_ns();
	pr_info("Hello World\n");
    delta = ktime_get_mono_fast_ns() - t0;

    if(time_values.count < 100){
        time_values.times[time_values.count++] = delta;
    }
   
	return 0;
}

static int __init kprobe_init(void)
{
	int ret;
	kp.pre_handler = handler_pre;

	ret = register_kprobe(&kp);
	if (ret < 0) {
		printk(KERN_INFO "register_kprobe failed, returned %d\n", ret);
		return ret;
	}
	printk(KERN_INFO "Planted kprobe at %p\n", kp.addr);

	ret = sysfs_create_file(kernel_kobj, &helloWorld_attr.attr);
	if(ret){
		pr_warn("Error while creating sysfs fils helloWorld\n");
		return -1;
	}
	return 0;
}

static void __exit kprobe_exit(void)
{
	unregister_kprobe(&kp);
	sysfs_remove_file(kernel_kobj, &helloWorld_attr.attr);
	printk(KERN_INFO "kprobe at %p unregistered\n", kp.addr);
}

module_init(kprobe_init)
module_exit(kprobe_exit)
MODULE_LICENSE("GPL");