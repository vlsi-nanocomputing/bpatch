/*
Code for test the patching function

Usage:
    ./bpatch <old_firmware> <patch> <new_firmware> <read_buffer_size> <patch_buffer_size>

*/

#include "main.h"

// define struct for flash memory 
typedef struct {
    uint8_t old_fw_slot[FW_SLOT_SIZE*1024];
    uint8_t new_fw_slot[FW_SLOT_SIZE*1024];
    uint8_t patch_slot[PATCH_SLOT_SIZE*1024];
} memory_t;

// instantiate memory
memory_t flash;

// addresses of the slots
uint64_t START_PATCH_SLOT;
uint64_t START_OLD_SLOT;  
uint64_t START_NEW_SLOT;

// buffer size
uint64_t READ_BUFFER_SIZE;
uint64_t PATCH_BUFFER_SIZE;


int main(int argc, char *argv[]){

    if (argc != 6) {
        printf("Usage: %s <old_firmware> <patch> <new_firmware> <read_buffer_size> <patch_buffer_size>\n", argv[0]);
        return 1;
    }

    // Initialize buffer sizes
    READ_BUFFER_SIZE = atoi(argv[4]);
    PATCH_BUFFER_SIZE = atoi(argv[5]);

    // Set memory addresses
    START_PATCH_SLOT = (uint64_t)flash.patch_slot;
    START_OLD_SLOT = (uint64_t)flash.old_fw_slot;  
    START_NEW_SLOT = (uint64_t)flash.new_fw_slot;

    // copy old firmware in memory
    FILE *file = fopen(argv[1], "rb");
    if (!file) {
        perror("Errore nell'apertura del file");
        return 1;
    }

    // Get file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    rewind(file);  // Torna all'inizio del file

    // Read file content and store in memory
    size_t bytes_read = fread(flash.old_fw_slot, 1, file_size, file);
    if (bytes_read != file_size) {
        perror("Errore nella lettura del file");
        fclose(file);
        return 1;
    }

    fclose(file);

    // Open patch file
    file = fopen(argv[2], "rb");
    if (!file) {
        perror("Errore nell'apertura del file");
        return 1;
    }

    // Get file size
    fseek(file, 0, SEEK_END);
    file_size = ftell(file);
    rewind(file);  // Torna all'inizio del file

    // Read file content and store in memory
    bytes_read = fread(flash.patch_slot, 1, file_size, file);
    if (bytes_read != file_size) {
        perror("Errore nella lettura del file");
        fclose(file);
        return 1;
    }

    fclose(file);

    // PATCHING
    file_size = bpatch();

    // write new firmware to file
    FILE *output_file = fopen(argv[3], "wb");
    if (!output_file) {
        perror("Errore nella creazione del file di output");
        return 1;
    }

    size_t bytes_written = fwrite(flash.new_fw_slot, 1, file_size, output_file);
    if (bytes_written != file_size) {
        perror("Errore nella scrittura del file");
        fclose(output_file);
        return 1;
    }

    fclose(output_file);

    return 0;
}