/*
 * bpatch.h
 *
 *  Created on: Feb 6, 2025
 *      Author: Andrea De Simone
 */
#ifndef __BPATCH_H__
#define __BPATCH_H__

#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* define to indicate test on CPU */
#define TEST_PATCH
/* define to indicate the presence of custom header of the firmware */
// #define HEADER_PATCH

#ifdef TEST_PATCH
/* addresses of the slots */
extern uint64_t START_PATCH_SLOT;
extern uint64_t START_OLD_SLOT;  
extern uint64_t START_NEW_SLOT;
/* buffer size */
extern uint64_t READ_BUFFER_SIZE;
extern uint64_t PATCH_BUFFER_SIZE;
#else
/* addresses of the slots */
#define START_PATCH_SLOT /* define start address patch slot */
#define START_OLD_SLOT /* define start address old fw slot */
#define START_NEW_SLOT /* define start address new fw slot */
/* buffer size */
#define READ_BUFFER_SIZE 1016
#define PATCH_BUFFER_SIZE 1024
#endif
// define write buffer size, must have 8 bytes more than read buffer size for alligment needed for flash write
#define WRITE_BUFFER_SIZE READ_BUFFER_SIZE + 8
#define HEADER_BYTE_SIZE 6

#define NEW_SLOT_LEN 0x2B000 // 172kB

/* verbose level: 0, no verbose; 1, percentage progress; 2, percentage progress and patch read*/
#define VERBOSE_LOG_PATCH 1

/* bit mask */
#define BIT_MASK(n) (1 << (7-n))

/* custom header defines and functions*/
#ifdef HEADER_PATCH

#define HEADER_FW_SIZE <N>    // size of the custum header in the firmware in bytes
#define HEADER_PATCH_SIZE <N> // size of the custom header in the patch in bits

void write_header(...);
#endif

/**
  * @brief This function writes the header of the firmware
  *
  * @param buffer: pointer to the buffer where the number will be read
  * @param pos: pointer to the bit position of the number in the buffer
  * @param index: pointer to the index of the buffer
  * @param len: bit length of the number in the buffer
  * @retval the number read
  */
uint32_t read_number(uint8_t *buffer, uint32_t *pos, uint32_t *index, uint8_t len);

/**
  * @brief This function writes the header of the firmware
  *
  * @param buffer: pointer to the buffer where the byte will be read
  * @param pos: pointer to the bit position of the byte in the buffer
  * @param index: pointer to the index of the buffer
  * @retval the byte read
  */
uint8_t read_byte(uint8_t *buffer, uint32_t *pos, uint32_t *index);

/**
  * @brief Main function to patch the firmware
  *
  */
int bpatch(void);

/* memory functions */
/**
  * @brief This function reads a amount of data from memory and copy into the output data buffer
  *
  * @param pDestination pointer of output data buffer
  * @param pSource pointer of memory address to read
  * @param uLength number of bytes to read
  * @return 0 when success
  */
int Mem_Read(void *pDestination, const void *pSource, uint32_t uLength);

/**
  * @brief This function writes a data buffer in internal or external flash
  *
  * @param pDestination pointer of flash memory to write. It has to be 8 bytes aligned.
  * @param pSource pointer on buffer with data to write
  * @param uLength length of data buffer in bytes. It has to be 8 bytes aligned.
  * @return 0 when success  */
int Mem_Write(void *pDestination, const void *pSource, uint32_t uLength);

/**
  * @brief This function erases a amount of internal or external flash pages depending of the length
  *
  * @param pStart pointer of memory address to erase
  * @param uLength number of bytes to erase
  * @return 0 when success  */
int Mem_Erase(void *pStart, uint32_t uLength);

/* print log functions */
void print_log(const char *format, ...);

#endif /*__BPATCH_H__*/