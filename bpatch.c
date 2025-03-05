/*
 * bpatch.c
 *
 *  Created on: Feb 6, 2025
 *      Author: Andrea De Simone
 */
#include "bpatch.h"

#ifdef TEST_PATCH

/* statistic to count read and write operations */
static int read_flash_op = 0;
static int write_flash_op = 0;
/* define to enable byte count during writing/reading */
// #define TEST_PATCH_RW_BYTE_COUNT

#endif

/* Memory functions */
int Mem_Read(void *pDestination, const void *pSource, uint32_t uLength){
#ifdef TEST_PATCH
	memcpy(pDestination, pSource, uLength);
    read_flash_op += 1;
#ifdef TEST_PATCH_RW_BYTE_COUNT
		printf("Read %d bytes\n", uLength);
#endif
    return 0;
#else
	/* memory read definition */
#endif
}

int Mem_Write(void *pDestination, const void *pSource, uint32_t uLength){
#ifdef TEST_PATCH
    memcpy(pDestination, pSource, uLength);
    write_flash_op += 1;
#ifdef TEST_PATCH_RW_BYTE_COUNT
	printf("Write %d bytes\n", uLength);
#endif
    return 0;
#else
	/* memory write definition */
#endif
}

int Mem_Erase(void *pStart, uint32_t uLength){
#ifdef TEST_PATCH
    memset(pStart, 255, uLength);
    return 0;
#else
	/* memory erase	definition */
#endif
}

#ifdef TEST_PATCH
    #define print_log(fmt, ...) printf(fmt, ##__VA_ARGS__)
#else
    void print_log(const char *format, ...) {
        /* print log definition */
    }
#endif

uint32_t read_number(uint8_t *buffer, uint32_t *pos, uint32_t *index, uint8_t len){
	uint32_t n = 0;

	// check if buffer is enough
	if ((*pos + len) > (PATCH_BUFFER_SIZE * 8)) {
		// shift the buffer
		memcpy(buffer, buffer + (*pos/8), PATCH_BUFFER_SIZE - (*pos/8));
		// fill the buffer
		Mem_Read((void *)&buffer[PATCH_BUFFER_SIZE - (*pos/8)], (const void *)(START_PATCH_SLOT + *index), *pos/8);
		*index += *pos/8;
		*pos %= 8;
	}

	for(int i=0; i<len; i++){
		n += ((buffer[(*pos+i)/8] & BIT_MASK((*pos+i)%8)) >> (7 - (*pos+i)%8)) << (len - 1 -i);
	}
	return n;
}


uint8_t read_byte(uint8_t *buffer, uint32_t *pos, uint32_t *index){
	uint16_t tmp;

	// check if buffer is enough
	if ((*pos + 8) > (PATCH_BUFFER_SIZE * 8)) {
		// shift the buffer
		memcpy(buffer, buffer + (*pos/8), PATCH_BUFFER_SIZE - (*pos/8));
		// fill the buffer
		Mem_Read((void *)&buffer[PATCH_BUFFER_SIZE - (*pos/8)], (const void *)(START_PATCH_SLOT + *index), *pos/8);
		*index += *pos/8;
		*pos %= 8;
	}

	tmp = (buffer[*pos/8] << 8) + buffer[*pos/8 + 1];
	return ((tmp<<(*pos%8)) & 0xffff) >> 8;
}

/* custom header functions*/
#ifdef HEADER_PATCH
void write_header(...){
	/* write header definition */
}
#endif // HEADER_PATCH


int bpatch(){
	uint8_t read_buffer[READ_BUFFER_SIZE], write_buffer[WRITE_BUFFER_SIZE], patch_buffer[PATCH_BUFFER_SIZE];
	uint32_t index_old = 0, index_new = 0, index_write = 0, index_buffer = 0, index_patch = 0, index_read = 0, write_byte, v, endpatch;
	uint8_t WNBD, WNBC, WNBA, CMD = 0, nb;

	// erase new fw slot
	Mem_Erase((void *)START_NEW_SLOT, NEW_SLOT_LEN);

	// read patch size and field byte length
	Mem_Read((void *)read_buffer, (const void *)(START_PATCH_SLOT + index_patch), HEADER_BYTE_SIZE);
	index_patch += HEADER_BYTE_SIZE;
	
	endpatch = read_buffer[0] + (read_buffer[1] << 8) + (read_buffer[2] << 16);
	WNBD = read_buffer[3];
	WNBC = read_buffer[4];
	WNBA = read_buffer[5];

	// fill the patch buffer
	Mem_Read((void *)patch_buffer, (const void *)(START_PATCH_SLOT + index_patch), PATCH_BUFFER_SIZE);
	index_patch += PATCH_BUFFER_SIZE;

	// fill the read buffer
	Mem_Read((void *)read_buffer, (const void *)(START_OLD_SLOT), READ_BUFFER_SIZE);

#ifdef HEADER_PATCH
	// write header
	write_header(...);
	
	// update indexes
	index_write += HEADER_FW_SIZE;
	index_buffer += HEADER_PATCH_SIZE;
	index_old += HEADER_FW_SIZE;
#endif

#ifdef HEADER_SBSFU
	// write header
	write_header(write_buffer, patch_buffer, patch_buffer + 4, patch_buffer + 4 + 32);

	// update indexes
	index_write += HEADER_FW_SIZE;
	index_buffer += HEADER_PATCH_SIZE;
	index_old += HEADER_FW_SIZE;
#endif

	// cycle until end of patch
	while ((index_patch * 8 - (PATCH_BUFFER_SIZE * 8) + index_buffer) < endpatch) {

#if (VERBOSE_LOG_PATCH == 1)
		// LOG patch percentage
		static int percentage_th = 0;
		static int percentage_value = 0;
		if ((index_patch * 8 - (PATCH_BUFFER_SIZE * 8) + index_buffer) > percentage_th){
            percentage_value = 100*(index_patch * 8 - (PATCH_BUFFER_SIZE * 8) + index_buffer)/endpatch;
			print_log("Patch percentage: %d\n", percentage_value);
			percentage_value+=10;
			percentage_th += endpatch/10;
		}
#endif

#if (VERBOSE_LOG_PATCH == 2)
		print_log("%u,", CMD);
#endif
		// CPY
		if (CMD == 0){
			// read nbd
			nb = read_number(patch_buffer, &index_buffer, &index_patch, WNBD);
			index_buffer += WNBD;
			if (nb) {
				v = read_number(patch_buffer, &index_buffer, &index_patch, nb);
				index_buffer += nb;
#if (VERBOSE_LOG_PATCH == 2)
				print_log("%u,", v);
#endif
				// skip bytes
				index_old += v;
			}
#if (VERBOSE_LOG_PATCH == 2)
			else
				print_log("0,");
#endif
			// read nbc
			nb = read_number(patch_buffer, &index_buffer, &index_patch, WNBC);
			index_buffer += WNBC;
			v = read_number(patch_buffer, &index_buffer, &index_patch, nb);
			index_buffer += nb;
#if (VERBOSE_LOG_PATCH == 2)
			print_log("%u\n\r", v);
#endif
			// write bytes
			while (v){
				write_byte = v >= READ_BUFFER_SIZE ? READ_BUFFER_SIZE : v;
				
				// check if 
				if (index_old > index_read + READ_BUFFER_SIZE) {
					// read from old firmware
					Mem_Read((void *)read_buffer, (const void *)(START_OLD_SLOT + index_old), READ_BUFFER_SIZE);
					index_read = index_old;
				}
				else if (write_byte > READ_BUFFER_SIZE - (index_old - index_read)) {
					// shift read buffer
					memcpy(read_buffer, read_buffer + (index_old - index_read), READ_BUFFER_SIZE - (index_old - index_read));
					// read from old firmware
					Mem_Read((void *)(read_buffer + READ_BUFFER_SIZE - (index_old - index_read)), (const void *)(START_OLD_SLOT + index_read + READ_BUFFER_SIZE), (index_old - index_read));
					index_read = index_old;
				}

				// check if write buffer is not enough
				if (index_write + write_byte > WRITE_BUFFER_SIZE) {
					Mem_Write((void *)(START_NEW_SLOT + index_new), (const void *)(write_buffer), index_write - (index_write%8));
					index_new += index_write - (index_write%8);
					// shift buffer
					memcpy(write_buffer, write_buffer + index_write - (index_write%8), index_write%8);
					index_write -= index_write - (index_write%8);
				}
				// copy
				memcpy(write_buffer + index_write, read_buffer + (index_old - index_read), write_byte);
				v -= write_byte;
				index_write += write_byte;
				index_old += write_byte;
			}
			CMD = 1;
		}
		// ADD
		else if (CMD == 1){
			// read nba
			nb = read_number(patch_buffer, &index_buffer, &index_patch, WNBA);
			index_buffer += WNBA;
			if (nb) {
				v = read_number(patch_buffer, &index_buffer, &index_patch, nb);
				index_buffer += nb;
#if (VERBOSE_LOG_PATCH == 2)
				print_log("%u", v);
#endif
				// add bytes
				while (v){
					// check if write buffer is not enough
					if (index_write > READ_BUFFER_SIZE) {
						Mem_Write((void *)(START_NEW_SLOT + index_new), (const void *)(write_buffer), index_write - (index_write%8));
						index_new += index_write - (index_write%8);
						// shift buffer
						memcpy(write_buffer, write_buffer + index_write - (index_write%8), index_write%8);
						index_write -= index_write - (index_write%8);
					}
					// read one bytes from the patch
					write_buffer[index_write] = read_byte(patch_buffer, &index_buffer, &index_patch);
#if (VERBOSE_LOG_PATCH == 2)
					print_log(",%02X", write_buffer[index_write]);
#endif
					index_buffer += 8;
					index_write++;
					v--;
				}
			}
#if (VERBOSE_LOG_PATCH == 2)
			else
				print_log("0");
			print_log("\n\r");
#endif
		CMD = 0;
		}

	}
	// fill write buffer with ones
	for (int i = index_write; i<(WRITE_BUFFER_SIZE); i++){
		write_buffer[i] = 0xff;
	}
	// finish to write buffer
	Mem_Write((void *)(START_NEW_SLOT + index_new), (const void *)(write_buffer), (WRITE_BUFFER_SIZE));
    index_new += index_write;

#if (VERBOSE_LOG_PATCH == 1)
    print_log("Patch percentage: 100\n");
#endif

#ifdef TEST_PATCH
    printf("Read Flash operations: %d\n", read_flash_op);
    printf("Write Flash operations: %d\n", write_flash_op);
#endif

    return index_new;
}