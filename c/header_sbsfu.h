/*
 * header_sbsfu.h
 *
 *  Created on: Mar 5, 2025
 *      Author: Andrea De Simone
 */

#ifndef __HEADER_SBSFU_H__
#define __HEADER_SBSFU_H__

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define PATCH_MAGIC 0x31554653
#define PATCH_VERSION 0x00010001;
#define HEADER_FW_SIZE 512
#define HEADER_PATCH_SIZE 800

/**
  * @brief This function writes the header of the firmware
  *
  * @param write_buffer: pointer to the buffer where the header will be written
  * @param size: pointer to the size of the new firmware
  * @param tag: pointer to the tag of the new firmware
  * @param sign: pointer to the sign of the new firmware
  * @retval None
  */
 void write_header(uint8_t *write_buffer, uint8_t *size, uint8_t *tag, uint8_t *sign);

#endif