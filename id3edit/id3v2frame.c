#include <errno.h> 
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
#include <id3v2.h>
#include <id3v2frame.h>
#include <endian.h>
#include <ConvertUTF/ConvertUTF.h>
#include <utfx.h>

#ifdef DEBUG
#include <printhex.h>
#endif

int ID3V2_GetTextFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int *size, char **utf8text)
{
    int error;

    // Get raw data
    unsigned int rawsize;
    void        *rawdata;
    error = ID3V2_GetFrame(id3v2, ID, &rawsize, &rawdata);
    if(error)
        return error;

    // Convert to utf8
    unsigned int   utf8size;
    unsigned char *utf8data;
    if(*(char*)rawdata == ID3V2TEXTENCODING_ISO8859_1) // this is ISO-8859-1 (!!! NOT \0 TERMINATED !!!)
    {
#ifdef DEBUG
        printhex(rawdata, rawsize, 16, 0, "\e[1;36m", 1, "\e[1;34m", -1);
        printf("\n");
#endif
        int isosize = rawsize - 1; // substract the encoding-byte

        error = ISO_8859_1toUTF8(&utf8data, &utf8size, rawdata, isosize);
        if(error)
        {
            free(rawdata);
            return error;
        }
    }
    else if(*(char*)rawdata == ID3V2TEXTENCODING_UTF16_BOM) // utf-16 with byte order mark as first char
    {
        // skip first byte because it contains the encoding info
        // also divide the size by two because we need the number of utf-16 chars, not the bytes
        unsigned short *utf16data = (unsigned short*)(((char*)rawdata)+1);
        unsigned int    utf16size = (rawsize - 1)/2;

        // Handle BOM
        // Because of some stupid shitty tools there may be 2 BOMs and they may be wrong m(
        // lets say, the last one counts, all leading are skipped
        unsigned short byteorder;
        while(*utf16data == UTF16BOM_BE || *utf16data == UTF16BOM_LE)
        {
            byteorder = *utf16data++;
            utf16size--; // one character less…
        }

#ifdef DEBUG
        printhex(rawdata, rawsize, 16, 
                0, "\e[1;36m", 
                1, "\e[1;33m\e[1;42m", 
                3, "\e[1;33m\e[1;41m", 
                5, "\e[1;34m", -1);
        printf("\n");
#endif
        // Convert
        error = UTF16toUTF8(&utf8data, &utf8size, utf16data, utf16size, byteorder);
        if(error)
        {
            free(rawdata);
            return error;
        }
    }
    else if(*(char*)rawdata == ID3V2TEXTENCODING_UTF16_BE)  // utf-16 big endian (and without leading BOM)
    {
        // skip first byte because it contains the encoding info
        // also divide the size by two because we need the number of utf-16 chars, not the bytes
        unsigned short *utf16data = (unsigned short*)(((char*)rawdata)+1);
        unsigned int    utf16size = (rawsize - 1)/2;

        // Handle BOM
        // Because of some stupid shitty tools there may be a BOM that shall not be in this frame m(
        // lets say, the last one counts, and they will not be ignored
        unsigned short byteorder = UTF16BOM_BE; // here, default is big endian
        while(*utf16data == UTF16BOM_BE || *utf16data == UTF16BOM_LE)
        {
            byteorder = *utf16data++;
            utf16size--; // one character less…
        }

#ifdef DEBUG
        printhex(rawdata, rawsize, 16, 
                0, "\e[1;36m", 
                1, "\e[1;33m\e[1;41m", 
                3, "\e[1;34m", -1);
        printf("\n");
#endif
        // Convert
        error = UTF16toUTF8(&utf8data, &utf8size, utf16data, utf16size, byteorder);
        if(error)
        {
            free(rawdata);
            return error;
        }
    }
    else if(*(char*)rawdata == ID3V2TEXTENCODING_UTF8)  // utf-8
    {
        utf8size = rawsize - 1 + 1; // -1: encoding, +1: \0
        utf8data = malloc(utf8size);
        if(utf8data == NULL)
        {
            free(rawdata);
            return ID3V2ERROR_FATAL;
        }
        memcpy(utf8data, ((char*)rawdata)+1, utf8size); // just copy, no transcoding necessary
        utf8data[utf8size-1] = '\0';
    }
    else // unsupported encoding
    {
        free(rawdata);
        return ID3V2ERROR_UNSUPPORTEDENCODING;
    }
    
    // free unneeded data
    free(rawdata);

    // Return everything
    if(size != NULL)
        *size = utf8size;
    if(utf8text != NULL)
        *utf8text = (char*)utf8data;

    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_SetTextFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int size, char *utf8text)
{
    int error;
    unsigned int    utf16length;    // number of character (not bytes)
    unsigned short *utf16data;

    // Convert utf8 to utf16
    error = UTF8toUTF16(&utf16data, &utf16length, (unsigned char*)utf8text, size);
    if(error)
    {
        return error;
    }
    
    // Create frame data (add enc-id and BOM)
    unsigned int rawsize = utf16length*2 + 3;   // char->byte + enc-ID + BOM
    void        *rawdata = malloc(rawsize);
    if(utf16data == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        free(utf16data);
        return ID3V2ERROR_FATAL;
    }

    ((unsigned char*)rawdata)[0] = 0x01; // encoding is UTF-16
    ((unsigned char*)rawdata)[1] = (UTF16BOM_LE >> 0) & 0xFF; // \_ BOM (Little Endian)
    ((unsigned char*)rawdata)[2] = (UTF16BOM_LE >> 8) & 0xFF; // /
    memcpy(((unsigned char*)rawdata)+3, utf16data, utf16length*2); // copy utf-16 string behind preamble

#ifdef DEBUG
    printhex(rawdata, rawsize, 16, 0, "\e[1;36m", 1, "\e[1;33m", 3, "\e[1;34m", -1);
    printf("\n");
#endif
    // Set Frame
    error = ID3V2_SetFrame(id3v2, ID, rawsize, rawdata);
    if(error)
    {
        free(rawdata);
        free(utf16data);
        return error;
    }
    
    // done
    free(rawdata);
    free(utf16data);

    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_GetPictureFrame(ID3V2 *id3v2, const unsigned char pictype, 
                          char **mimetype, char **description, void **picture, unsigned int *picsize)
{
    int error;

    // Get raw data
    unsigned int rawsize;
    int          rawoffset = 0;  // traceing offset through the process to know where we are in the frame
    void        *rawdata;
    error = ID3V2_GetFrame(id3v2, 'APIC', &rawsize, &rawdata);
    if(error)
        return error;

    // Read header
    unsigned char *rawbytes = (unsigned char*)rawdata;
    
    // encoding - 0x00: ISO 8859-1; 0x01: UTF-16
    unsigned char encoding = *rawbytes;
    rawoffset += 1;
    
    // mime-type - ASCII encoded, '\0'-terminated
    int  mimesize = strlen((char*)(rawbytes+rawoffset));
    char *mime    = (char*)malloc(mimesize+1); // +'\0'
    if(mime == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }
    strncpy(mime, (char*)(rawbytes+rawoffset), mimesize+1); // at offset 1 all chars + '\0'
    rawoffset += mimesize + 1; // mimetype-string + '\0'
    
    // picture type
    unsigned char picturetype = *(rawbytes + rawoffset);
    if(picturetype != pictype) // is this the one the user wants to have?
    {
        free(mime);
        fprintf(stderr, "Multiple APIC-frames are not supported yet!\n");
        return ID3V2ERROR_MISFITTINGSUBID;
    }
    rawoffset += 1; // pictype

    // text description SPEC SAYS: (raw data: max 64 chars + '\0[\0]' -> max 65*2 bytes = 130bytes)
    unsigned char *desctext; // utf-8 encoded \0-terminated string
    int            descsize; // number of bytes of the original description in the file (for offset calculation)
    if(encoding == 0x00) // ISO 8859-1
    {
        // extract raw data
        char *descdata;
        descdata = malloc(sizeof(char)*65); // just alloc max length
        if(descdata == NULL)
        {
            fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
            return ID3V2ERROR_FATAL;
        }
        strncpy(descdata, (char*)(rawbytes + rawoffset), 65);
        descsize   = strlen(descdata) + 1; // number of bytes of the description for offset calculation 
        rawoffset += descsize;

        // convert to utf-8
        error = ISO_8859_1toUTF8(&desctext, NULL, (unsigned char*)descdata, strlen(descdata));
        if(error)
        {
            free(descdata);
            return error;
        }
        free(descdata); // raw data not needed anymore
    }
    else // UTF-8
    {
        // extract raw data
        unsigned short *descdata;
        descdata = malloc(sizeof(char)*130); // just alloc max length
        if(descdata == NULL)
        {
            fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
            return ID3V2ERROR_FATAL;
        }

        // copy utf-16 data
        unsigned short BOM     = *(unsigned short*)(rawbytes + rawoffset);
        rawoffset             += 2; // BOM
        unsigned short *source =  (unsigned short*)(rawbytes + rawoffset);
        for(int i=0; i<65; i++) // max 64 chars + '\0\0'
        {
            descdata[i] = source[i];
            descsize   += 2; // 2 bytes per char
            if(descdata[i] == 0x0000) break;
        }
        rawoffset += descsize;

        // convert to utf-8
        int utf16length = (descsize-2)/2; // number of chars, '\0\0' excluded
        error = UTF16toUTF8(&desctext, NULL, descdata, utf16length, BOM);
        if(error)
        {
            free(descdata);
            return error;
        }
        free(descdata); // raw data not needed anymore
    }

#ifdef DEBUG
    if(encoding == 0x01)
    {
        printhex(rawdata, 128, 16, 
            0,                          "\e[1;36m", // encoding
            1,                          "\e[1;35m", // mime-type
            1+mimesize+1,               "\e[1;32m", // pictype
            1+mimesize+1+1,             "\e[1;33m", // BOM
            1+mimesize+1+1+2,           "\e[0;35m", // description
            1+mimesize+1+1+2+descsize,  "\e[1;34m", // pic-data
            -1);
    }
    else // ISO8859-1
    {
        printhex(rawdata, 128, 16, 
            0,                        "\e[1;36m", // encoding
            1,                        "\e[1;35m", // mime-type
            1+mimesize+1,             "\e[1;32m", // pictype
            1+mimesize+1+1,           "\e[0;35m", // description
            1+mimesize+1+1+descsize,  "\e[1;34m", // pic-data
            -1);
    }
    printf("\n");
#endif

    // now just copy the picture into a buffer
    unsigned char *picdata;
    unsigned int   picdatasize = rawsize-rawoffset;
    picdata = malloc(picdatasize);
    if(picdata == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }
    memcpy(picdata, rawdata+rawoffset, picdatasize);
    

    if(mimetype != NULL)
        *mimetype = mime;
    if(description != NULL)
        *description = (char*)desctext;
    if(picture != NULL)
        *picture = picdata;
    if(picsize != NULL)
        *picsize = picdatasize;

    free(rawdata);
    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_SetPictureFrame(ID3V2 *id3v2, const unsigned char pictype, 
                          const char *mimetype, const char *description,
                          void *picture, unsigned int picsize)
{
    int error;
    // collect all infos for the frame and convert description to utf16 data
    unsigned int utf16length; // num of characters, no trailing zeros
    unsigned short *utf16data;
    if(description != NULL)
    {
        error = UTF8toUTF16(&utf16data, &utf16length, (unsigned char*)description, strlen(description));
        if(error)
            return error;
    }
    else // create empty utf16 string - 0-terminated
    {
        utf16length = 0;
        utf16data   = (unsigned short*) malloc(2);
        if(utf16data == NULL)
        {
            fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
            return ID3V2ERROR_FATAL;
        }
        *utf16data = 0x0000;
    }

    // calculate framesize
    unsigned int framesize = 0;
    framesize += 1; // encoding
    framesize += strlen(mimetype) + 1; // mimetype + '\0'
    framesize += 1; // pictype
    framesize += 2; // BOM
    framesize += utf16length*2;     // description length in byte
    framesize += 2; // '\0\0'
    framesize += picsize;

    // create framdata
    unsigned char *framedata = malloc(framesize);
    if(framedata == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        free(utf16data);
        return ID3V2ERROR_FATAL;
    }

    unsigned int frameoffset = 0;
    framedata[frameoffset++] = 0x01;                // encoding: UTF-16
    strcpy((char*)(framedata+frameoffset), mimetype);        // mimetype
    frameoffset += strlen(mimetype)+1;
    framedata[frameoffset++] = pictype;             // pictype (should be 0x03 - front cover)
    framedata[frameoffset++] = (UTF16BOM_LE >> 0) & 0xFF; // \_ BOM (little endian)
    framedata[frameoffset++] = (UTF16BOM_LE >> 8) & 0xFF; // /
    memcpy(framedata+frameoffset, utf16data, utf16length*2);    // utf16 encoded description
    frameoffset += utf16length*2;
    framedata[frameoffset++] = 0x00;                // first trailing \0 of the description
    framedata[frameoffset++] = 0x00;                // secound trailing \0 of the description
    memcpy(framedata+frameoffset, picture, picsize);// picture

#ifdef DEBUG
    unsigned int mimesize = strlen(mimetype);
    printhex(framedata, 128, 16, 
            0,                          "\e[1;36m", // encoding
            1,                          "\e[1;35m", // mime-type
            1+mimesize+1,               "\e[1;32m", // pictype
            1+mimesize+1+1,             "\e[1;33m", // BOM
            1+mimesize+1+1+2,           "\e[0;35m", // description
            1+mimesize+1+1+2+utf16length*2+2, "\e[1;34m", // pic-data
            -1);
    printf("\n");
#endif
    // set frame
    error = ID3V2_SetFrame(id3v2, 'APIC', framesize, framedata);
    if(error)
    {
        free(framedata);
        free(utf16data);
        return error;
    }

    // done
    free(framedata);
    free(utf16data);
    return ID3V2ERROR_NOERROR;
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

