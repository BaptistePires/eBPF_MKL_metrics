KERNELDIR_PNL ?=/media/baptiste/hdd/Cours/CoursS2/psar/kernel/linux-5.10.17

PWD := $(shell pwd)

obj-m += helloWorld.o

all :
	make -C $(KERNELDIR_PNL) M=$(PWD) modules

clean:
	make -C $(KERNELDIR_PNL) M=$(PWD) clean

