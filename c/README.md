C source code to apply the patch and reconstruct the new firmware. The application read and write from generic flash memory, it is possible to define the read/write functions.
To test the code it is created a wrapper where the memory region is mapped on the stack, firmwares and patch are passed as files. To enable the wrapper you have to 
enable the MACRO **TEST_PATCH**

## How to use

- usage when macro **TEST_PATCH** is enabled

       ./bpatch <old_firmware> <patch> <new_firmware> <read_buffer_size> <patch_buffer_size>

- usage for MCU or generic porcessor

    - copy *bpatch.c* and *bpatch.h*
    - add definition of memory functions and log function
    - add memory address of old firmware slot, new firmware slot and pacth slot
    - remove define **TEST_PATCH**
    - use with:

            bpatch();

## Custom header

In *header_sbsfu.c* and *header_sbsfu.h* are present an example of custom header function and defines based on SBSFU expansion packet for STM32 detailed [here](https://www.st.com/en/embedded-software/x-cube-sbsfu.html) 