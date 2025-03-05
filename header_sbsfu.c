/*
 * header_sbsfu.c
 *
 *  Created on: Mar 5, 2025
 *      Author: Andrea De Simone
 */

 #include "header_sbsfu.h"

 void write_header(uint8_t *write_buffer, uint8_t *size, uint8_t *tag, uint8_t *sign){
	// header size of 512 bytes, so buffer size must be at least 512

	uint32_t buffer[48];
	// write SFUMagic
	buffer[0] = PATCH_MAGIC;
	memcpy(write_buffer, buffer, 4);

	// write ProtocolVersion and FwVersion
	buffer[0] = PATCH_VERSION;
	memcpy(write_buffer + 4, buffer, 4);

	// write FwSize
	memcpy(write_buffer + 8, size, 4);
	// write PartialFwOffset
	buffer[0] = 0;
	memcpy(write_buffer + 12, buffer, 4);
	// write PartialFwSize
	memcpy(write_buffer + 16, size, 4);

	// write FwTag
	memcpy(write_buffer + 20, tag, 32);
	// write PartialFwTag
	memcpy(write_buffer + 52, tag, 32);

	// write Reserved
	for(int i=0;i<11; i++) buffer[i] = 0;
	memcpy(write_buffer + 84, buffer, 44);

	// write HeaderSignature
	memcpy(write_buffer + 128, sign, 64);

	// write FwImageState
	for(int i=0;i<24; i++) buffer[i] = 0xffffffff;
	memcpy(write_buffer + 192, buffer, 96);

	// write PrevHeaderFingerprint
	for(int i=0;i<8; i++) buffer[i] = 0;
	memcpy(write_buffer + 288, buffer, 32);

	for(int i=0;i<48; i++) buffer[i] = 0xffffffff;
	memcpy(write_buffer + 320, buffer, 192);
}