KERNELDIR_PNL ?=/share/linux
PWD := $(shell pwd)
CFLAGS  := -O2
obj-m += count.o

all :
	make -C $(KERNELDIR_PNL) M=$(PWD) modules

clean:
	make -C $(KERNELDIR_PNL) M=$(PWD) clean

