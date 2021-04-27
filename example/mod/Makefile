KERNEL_SRC ?=/media/baptiste/hdd/Cours/CoursS2/psar/kernel/linux-5.10.17

PWD := $(shell pwd)

obj-m += helloWorld.o

all :
	make -C $(KERNEL_SRC) M=$(PWD) modules

clean:
	make -C $(KERNEL_SRC) M=$(PWD) clean

