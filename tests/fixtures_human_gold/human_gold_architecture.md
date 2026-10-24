# Linux Kernel Network Scaling: Receive Packet Steering (RPS)

**Source:** Tom Herbert. *Linux Kernel Documentation: Documentation/networking/scaling.rst*. Git commit: torvalds/linux.

Receive Packet Steering (RPS) is logically a software implementation of RSS. Being in software, it is necessarily called later in the data path. Whereas RSS selects the queue and hence CPU that will run the hardware interrupt handler, RPS selects the CPU to perform protocol processing above the interrupt handler. This is accomplished by hashing the packet headers to determine the target CPU.

RPS has several advantages over multi-queue NICs. First, it can be used with any network interface card. Second, it is easy to add new hashing protocols. Third, it does not increase the hardware interrupt rate, though it does introduce inter-processor interrupts (IPIs).

RPS is configured per receive queue. Each queue has an entry in sysfs that contains a bitmap of CPUs that may process traffic for that queue. When a packet is received, the CPU calculates a hash over the network packet headers. The hash is used as an index into the CPU bitmap, and an IPI is sent to the target CPU to process the packet in softirq context.
