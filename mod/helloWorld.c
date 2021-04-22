#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
/**
 * Simple module that triggers at each printk calls.
 * Source : https://github.com/spotify/linux/blob/master/samples/kprobes/kprobe_example.c
 **/


struct store_time {
    ktime_t times[100];
    __u8 count;
}static time_values;

// Target (symbol)
static struct kprobe kp = {
	.symbol_name	= "printk",
};

static int handler_pre(struct kprobe *p, struct pt_regs *regs)
{
    ktime_t t0, delta;
    t0 = ktime_get();
	pr_info("Hello World\n");
    delta = ktime_get() - t0;

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
	return 0;
}

static void __exit kprobe_exit(void)
{
	unregister_kprobe(&kp);
	printk(KERN_INFO "kprobe at %p unregistered\n", kp.addr);
}

module_init(kprobe_init)
module_exit(kprobe_exit)
MODULE_LICENSE("GPL");