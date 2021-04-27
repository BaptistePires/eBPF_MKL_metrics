#include <linux/init.h>
#include <linux/module.h>
#include <linux/types.h>
#include <linux/kernel.h>
#include <linux/moduleparam.h>
#include <linux/tracepoint.h>
#include <linux/fdtable.h>

//https://tuxthink.blogspot.com/2012/05/module-to-print-open-files-of-process.html
//https://stackoverflow.com/questions/66322265/using-printk-in-tracepoint-causes-the-system-to-freeze

MODULE_DESCRIPTION("Module \"hello world param\"");
MODULE_AUTHOR("Leif Henriksen");
MODULE_LICENSE("GPL");

//static char* tp_name="Default";
//module_param(tp_name, charp, 0660);

static struct tracepoint * mon_tp = NULL;
static char* tp_name = "ext4_da_write_begin";

static void lookup_tps(struct tracepoint *tp, void *priv){
  if(strcmp(tp->name, tp_name) == 0){
      mon_tp = tp;
  }
}

static void print_all_events(struct tracepoint *tp, void *priv){
  printk("tp_test : %s\n", tp->name);
}

static void probe(struct inode *inode, loff_t pos, unsigned int len,
		  unsigned int flags)
{
  int i=0;
  struct fdtable *files_table;
  struct path file_path;

  //current ?
  files_table = files_fdtable(current->files);

  //pos c'est l'@ de inode ??!!!!
  //printk("inode = %ld\n", ((struct inode*)pos)->i_ino);
  while(files_table->fd[i] != NULL)
    {

      if(files_table->fd[i]->f_inode == NULL)
	{
	  printk("NULL f_inode\n");
	  i++;
	  continue;
	}
      
      if(files_table->fd[i]->f_inode->i_ino == ((struct inode*)pos)->i_ino)
      {
        file_path = files_table->fd[i]->f_path;
        printk("tp_test : probe ext4_da_write_begin : writing in %s, fd = %i, inode = %ld, len = %u, flags = %u\n",
	       file_path.dentry->d_iname, i, ((struct inode*)pos)->i_ino, len, flags);
	break;
      }
      i++;
    }  
}

//include/trace/events/ext4.h
//Pour ext4_writepage
//Ne fait rien ?!
/*
static void probe(struct page *page)
{
  printk("tp_test : probe\n");
}
*/

//Pour ext4_request_inode
/*
static void probe(struct inode *dir, int mode)
{
  printk("tp_test : probe\n");
}
*/
static int __init tp_test_init(void)
{
  printk("tp_test : init\n");

  for_each_kernel_tracepoint(lookup_tps, NULL);

  if(mon_tp != NULL)
    {
      printk("tp_test : %s found\n", tp_name);
    }
  else
    {
      printk("tp_test : Error: %s not found\n", tp_name);
      return -1;
    }
  
   if(tracepoint_probe_register(mon_tp, probe, NULL) != 0)
     {
       printk(KERN_INFO "regist fail.\n");
       return -1;
     }
   
   return 0;
}
module_init(tp_test_init);

static void __exit tp_test_exit(void)
{
  tracepoint_probe_unregister(mon_tp, probe, NULL);
  printk("tp_test : exit\n");
}
module_exit(tp_test_exit);

