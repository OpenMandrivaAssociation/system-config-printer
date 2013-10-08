/* 
 * This program simply returns the uri of an usb device by using libhpmud.
 * It allows us to install hal-cups-utils without requiring whole hplip.
 * syntax: hp-makeuri-mdv bus device
 * example: hp-makeuri-mdv 002 018
 * These values can be obtained from lsusb.
 *
 * Tiago Salem Herrmann <salem@mandriva.com>
 */

#include <stdio.h>
#define HPMUD_BUFFER_SIZE 8192

enum HPMUD_RESULT
{
   HPMUD_R_OK = 0,
   HPMUD_R_INVALID_DEVICE = 2,
   HPMUD_R_INVALID_DESCRIPTOR = 3,
   HPMUD_R_INVALID_URI = 4,
   HPMUD_R_INVALID_LENGTH = 8,
   HPMUD_R_IO_ERROR = 12,
   HPMUD_R_DEVICE_BUSY = 21,
   HPMUD_R_INVALID_SN = 28,
   HPMUD_R_INVALID_CHANNEL_ID = 30,
   HPMUD_R_INVALID_STATE = 31,
   HPMUD_R_INVALID_DEVICE_OPEN = 37,
   HPMUD_R_INVALID_DEVICE_NODE = 38,
   HPMUD_R_INVALID_IP = 45,
   HPMUD_R_INVALID_IP_PORT = 46,
   HPMUD_R_INVALID_TIMEOUT = 47,
   HPMUD_R_DATFILE_ERROR = 48,
   HPMUD_R_IO_TIMEOUT = 49,
};
enum HPMUD_RESULT hpmud_make_usb_uri(const char *busnum, const char *devnum, char *uri, int uri_size, int *bytes_read);

int main(int argc, char **argv)
{
    if (argc != 3)
        return 1;

    char * busnum = argv[1];
    char * devnum = argv[2];
    char uri[HPMUD_BUFFER_SIZE];
    enum HPMUD_RESULT result = HPMUD_R_OK;
    int bytes_read = 0;
    
    result = hpmud_make_usb_uri(busnum, devnum, uri, HPMUD_BUFFER_SIZE, &bytes_read);
    if(result)
        return 1;
    printf("%s\n", uri);
    return 0;
}

