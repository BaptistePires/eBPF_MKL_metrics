#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
/**
 * Simple module that triggers at each printk calls.
 * Source : https://github.com/spotify/linux/blob/master/samples/kprobes/kprobe_example.c
 **/

// Target (symbol)
static struct kprobe kp = {
	.symbol_name	= "printk",
};

static int handler_pre(struct kprobe *p, struct pt_regs *regs)
{
	pr_info("Hello World\n");
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