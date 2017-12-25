#include <errno.h> 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <endian.h>
#include <ConvertUTF/ConvertUTF.h>
#include <id3v2.h>
#include <utfx.h>

#ifdef DEBUG
#include <printhex.h>
#endif

int ISO_8859_1toUTF8(unsigned char **utf8, unsigned int *utf8size,
                     unsigned char *ISO8859, unsigned int ISO8859size)
{
    // ISO 8859-1: 0x20..0x7F, 0xA0..0xFF
    // calc max length for utf-8 string
    int size=0;
    for(int i=0; i<=ISO8859size; i++)
    {
             if(ISO8859[i] >= 0x20 && ISO8859[i] <= 0x7F) size++;
        else if(ISO8859[i] >= 0xA0 && ISO8859[i] <= 0xFF) size+=2;
    }

    unsigned char *utf8data = (unsigned char*) malloc(size + 1); // +1 for '\0'
    if(utf8data == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }
    
    // Source: http://stackoverflow.com/questions/4059775/convert-iso-8859-1-strings-to-utf-8-in-c-c
    int utf8index = 0;
    for(int i=0; i<=ISO8859size; i++)
    {
        if(ISO8859[i] >= 0x20 && ISO8859[i] <= 0x7F)
        {
            utf8data[utf8index++] = ISO8859[i];
        }
        else if(ISO8859[i] >= 0xA0 && ISO8859[i] <= 0xFF)
        {
            utf8data[utf8index++] = 0xC2 | (ISO8859[i]>0xBF);
            utf8data[utf8index++] = 0x80 | (ISO8859[i]&0x3F);
        }
        
    }

    // append '\0' to be save
    utf8data[size] = '\0'; // utf8data ist one byte longer that size
    
    if(utf8 != NULL)
       *utf8 = utf8data;
    if(utf8size != NULL)
        *utf8size = size;

    return ID3V2ERROR_NOERROR;
}

/*
Source: http://stackoverflow.com/questions/4059775/convert-iso-8859-1-strings-to-utf-8-in-c-c
unsigned char *in, *out;
while (*in)
        if (*in<128) *out++=*in++;
            else *out++=0xc2+(*in>0xbf), *out++=(*in++&0x3f)+0x80;
*/

//////////////////////////////////////////////////////////////////////////////

int UTF16toUTF8(unsigned char  **utf8,  unsigned int *utf8length, 
                unsigned short  *utf16, unsigned int  utf16length, unsigned short BOM)
{
    ConversionResult result;
    UTF16 *utf16start = utf16;
    UTF16 *utf16end   = utf16+utf16length;
    UTF8  *utf8start  = malloc(utf16length*2 + 1024); // utf-16 -> utf-8 can compress OR expand the buffer…
    UTF8  *utf8string = utf8start;    // utf8start will be overwritten by the convert function
    UTF8  *utf8end    = utf8start + utf16length*2 + 1024;

    // check if allocation was successfull
    if(utf8start== NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }

    // Handle BOM: This fucking conversion library doesn't do it. >:(
    // Convert utf-16 string to little endian
    if(BOM == UTF16BOM_BE)
    {
        UTF16BEtoUTF16LE(utf16, utf16length);
    }

    // Convert
    result = ConvertUTF16toUTF8((const UTF16**)&utf16start, (const UTF16*)utf16end,
                                &utf8start, utf8end, strictConversion);
    if(result != conversionOK)
    {
        fprintf(stderr, "ERROR: utf-16 -> utf-8 conversion failed with error: ");
        switch(result)
        {
            case sourceExhausted:
                fprintf(stderr, "Source Exhausted (partial Character in source, but hit end)");
                break;
            case targetExhausted:
                fprintf(stderr, "Target Exhausted (insufficient room in target for conversion)");
                break;
            case sourceIllegal:
                fprintf(stderr, "Source Illegal (source sequence is illegal/malformed)");
                break;
            default:
                fprintf(stderr, "Fatal Error! Unexpected return value from ConvertUTF16toUTF8!");
                break;
        }
        fprintf(stderr, "\n");

        return ID3V2ERROR_UNICODEERROR;
    }

    // append '\0'
    *utf8start = '\0'; // this is save because the convert function sets the pointer to the end

    // Return all data
    if(utf8 != NULL)
        *utf8 = utf8string;
    if(utf8length != NULL)
        *utf8length = strlen((char*)utf8string);

    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

#define SWAPBYTES(w) ((((w)&0x00FF)<<8)|(((w)&0xFF00)>>8))
void UTF16BEtoUTF16LE(unsigned short *utf16, unsigned int utf16length)
{
    for(unsigned int i=0; i<utf16length; i++)
    {
        utf16[i] = SWAPBYTES(utf16[i]);
    }
}

//////////////////////////////////////////////////////////////////////////////

int UTF8toUTF16(unsigned short **utf16, unsigned int *utf16length, 
                unsigned char   *utf8,  unsigned int  utf8length)
{
    unsigned int utf16len = utf8length*2 + 1024; // hard to tell… but 2 utf16 per utf8 + buffer may be ok
    UTF8  *utf8start  = utf8;
    UTF8  *utf8end    = utf8 + utf8length;
    UTF16 *utf16start = malloc(sizeof(UTF16)*utf16len); 
    UTF16 *utf16data  = utf16start; // to not loose the starting point
    UTF16 *utf16end   = utf16start + utf16len;

    // check if allocation was successfull
    if(utf16start== NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }

    ConversionResult result;
    result = ConvertUTF8toUTF16((const UTF8**)&utf8start, (const UTF8*)utf8end, 
                                &utf16start, utf16end, strictConversion);
    if(result != conversionOK)
    {
        fprintf(stderr, "ERROR: utf-16 -> utf-8 conversion failed with error: ");
        switch(result)
        {
            case sourceExhausted:
                fprintf(stderr, "Source Exhausted (partial Character in source, but hit end)");
                break;
            case targetExhausted:
                fprintf(stderr, "Target Exhausted (insufficient room in target for conversion)");
                break;
            case sourceIllegal:
                fprintf(stderr, "Source Illegal (source sequence is illegal/malformed)");
                break;
            default:
                fprintf(stderr, "Fatal Error! Unexpected return value from ConvertUTF16toUTF8!");
                break;
        }
        fprintf(stderr, "\n");

        return ID3V2ERROR_UNICODEERROR;
    }

    if(utf16 != NULL)
        *utf16 = utf16data;
    if(utf16length != NULL)
        *utf16length = utf16start - utf16data;
        // utf16start gets manipulated by the Convert-Function and points to the end
        // just calculate the difference to get the number of characters (difference of elements!!! not bytes)

    return ID3V2ERROR_NOERROR;
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

