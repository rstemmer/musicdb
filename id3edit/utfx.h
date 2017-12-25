#ifndef UTFX_H
#define UTFX_H


#define UTF16BOM_LE 0xFEFF
#define UTF16BOM_BE 0xFFFE

int ISO_8859_1toUTF8(unsigned char **utf8, unsigned int *utf8size,
                     unsigned char *ISO8859, unsigned int ISO8859size);

int UTF16toUTF8(unsigned char  **utf8,  unsigned int *utf8length,
                unsigned short  *utf16, unsigned int  utf16length, unsigned short BOM);
/*
 * this function also allocates memory for the utf8 data
 * the length is in character, not in byte
 */
    
void UTF16BEtoUTF16LE(unsigned short *utf16, unsigned int utf16length);

int UTF8toUTF16(unsigned short **utf16, unsigned int *utf16length,
                unsigned char   *utf8,  unsigned int  utf8length);

#endif



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

