#ifndef ID3V2_H
#define ID3V2_H

#include <stdio.h>
#include <stdbool.h>

#define ID3V2PADDING    2048    // number of padding bytes at the end - maybe some tools want to have some

#define ID3V2ERROR_NOERROR           0  // no error - all is good
#define ID3V2ERROR_FATAL        -1000   // if malloc returns NULL or other worst case errors (better to exit(-1))
#define ID3V2ERROR_PATHERROR        -1  // problem with the path (for example fopen failed)
#define ID3V2ERROR_NOTSUPPORTED     -2
#define ID3V2ERROR_FRAMENOTFOUND    -3
#define ID3V2ERROR_UNICODEERROR     -4
#define ID3V2ERROR_MISFITTINGSUBID  -5
#define ID3V2ERROR_WRITEERROR       -6
#define ID3V2ERROR_UNEXPECTEDEOF    -7
#define ID3V2ERROR_UNSUPPORTEDENCODING -8

#define ID3V2HEADERFLAG_UNSYNCHRONISATION (1<<7)
#define ID3V2HEADERFLAG_EXTENDEDHEADER    (1<<6)
#define ID3V2HEADERFLAG_EXPERIMENTAL      (1<<5)
#define ID3V2HEADERFLAG_FOOTER            (1<<4) /*indicates a footer - new in 2.4*/

#define ID3V2ID_TO_CHARS(i) (((i)>>24)&0xFF),(((i)>>16)&0xFF),(((i)>> 8)&0xFF),(((i)>> 0)&0xFF)

// all structs are interpeted and decoded versions of the raw data
typedef struct
{
    unsigned char ID[3];                     // 'ID3' - no 0-byte at the end!
    unsigned char version_major;    // 3 \_ for ID3v2.3.0
    unsigned char version_minor;    // 0 /
    unsigned char flags;            // ID3V2HEADERFLAG_*
    unsigned int  origsize;         // size of the ID3 infos as stored in the files header
    unsigned int  realsize;         // sum of all read ID3 data (incl. frame-header) excluding padding bytes
                                    //   realsize will be alway up to date after changing frames, 
                                    //   origsize will never change
} ID3V2_HEADER;

typedef struct
{
    unsigned int   size;
    unsigned short flags;
    unsigned int   paddingsize;
} ID3V2_EXTHEADER;

#define ID3V2FRAMEFLAG_DISCARD_FRAME    (1<<15)
#define ID3V2FRAMEFLAG_DISCARD_FILE     (1<<14)
#define ID3V2FRAMEFLAG_READONLY         (1<<13)
#define ID3V2FRAMEFLAG_COMPRESSED       (1<< 7)
#define ID3V2FRAMEFLAG_ENCRYPTED        (1<< 6)
#define ID3V2FRAMEFLAG_FRAMEGROUP       (1<< 5)
typedef struct
{
    unsigned int   ID;
    unsigned int   size;
    unsigned short flags;   // ID3V3FRAMEFLAG_*
    void*          data;    // Data of the frame
    struct ID3V2_FRAME *next;
} ID3V2_FRAME;

typedef struct
{
    char *path;     // path of the filename
    FILE *file;     // file pointer
    
    ID3V2_HEADER    header;    // Header of the ID3 information
    ID3V2_EXTHEADER extheader; // Extended Header
    ID3V2_FRAME *framelist; // List of all ID3 Frames
} ID3V2;

//////////////////////////////////////////////////////////////////////////////

extern bool OPT_PrintHeader;    // print header detail while reading the ID3 tag

//////////////////////////////////////////////////////////////////////////////

int ID3V2_Open(ID3V2 **id3v2, const char *path, bool createtag);
/*
 * Opens the file and reads all the ID3 information.
 * The infos are stored in a new allocated ID3V2 struct thats address will be written 
 * to the id3v2 pointer and so be propergated to the user.
 * The path must be an absolute path!
 * if createtag is true, and the file is a mp3 file (0xFF 0xFB as magic word) a new ID3v2 Tag is generated
 *
 *  # int error;
 *  # ID3V2 *id3v2 = NULL;
 *  # error = ID3V2_Open(&id3v2, "/tmp/test.mp3", true);
 */


int ID3V2_Close(ID3V2 *id3v2, const char *altpath);
/*
 * After storing (recreating) the ID3v2 infos the id3v2 struct will be freed - id3v2 is no more valid after
 * closing the file
 * If altpath is != NULL, the data will be written to a new file, otherwise the old file gets overwritten
 * The path must be absolute
 * If altpath is "/dev/null" nothing will be written (even not to /dev/null) - this is readonly-mode :)
 *
 *  # error  = ID3V2_Close(id3v2, NULL);
 *  # *id3v2 = NULL;
 */

int ID3V2_RemoveAllFrames(ID3V2 *id3v2);
/*
 * Remove all frames
 */

int ID3V2_GetFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int *size, void **data);
/*
 * the size of the frame gets returned by writing to the size pointer
 * for data, new memory gets allocated and a copy of the data will be created.
 * If not used anymore, the user has to free the data memory
 * If an error occures, do not call free on data
 *
 * # int  size;
 * # char *title;
 * # error = ID3V2_GetFrame(id3v2, 'TIT2', &size, &title);
 * #
 * # // do something
 * #
 * # free(*title);
 * # *title = NULL;
 */

int ID3V2_SetFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int size, void *data);
/*
 * # error = ID3V2_SetFrame(id3v2, 'TIT2', size, title);
 */


#endif



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

