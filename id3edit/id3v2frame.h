#ifndef ID3V2FRAME_H
#define ID3V2FRAME_H

#define ID3V2TEXTENCODING_ISO8859_1 0x00    /* 0x20 … 0xFF */
#define ID3V2TEXTENCODING_UTF16_BOM 0x01    /* utf-16 starting with an byte order mark */
#define ID3V2TEXTENCODING_UTF16_BE  0x02    /* utf-16 big endian */
#define ID3V2TEXTENCODING_UTF8      0x03    /* utf-8 */

#define ID3V2_GetTitle(i,s,t)  ID3V2_GetTextFrame(i, 'TIT2', s, t)
#define ID3V2_GetAlbum(i,s,t)  ID3V2_GetTextFrame(i, 'TALB', s, t)
#define ID3V2_GetArtist(i,s,t) ID3V2_GetTextFrame(i, 'TPE1', s, t)
#define ID3V2_GetYear(i,s,t)   ID3V2_GetTextFrame(i, 'TYER', s, t)
#define ID3V2_GetTrack(i,s,t)  ID3V2_GetTextFrame(i, 'TRCK', s, t)
#define ID3V2_GetCD(i,s,t)     ID3V2_GetTextFrame(i, 'TPOS', s, t)

int ID3V2_GetTextFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int *size, char **utf8text);



#define ID3V2_SetTitle(i,s,t)  ID3V2_SetTextFrame(i, 'TIT2', s, t)
#define ID3V2_SetAlbum(i,s,t)  ID3V2_SetTextFrame(i, 'TALB', s, t)
#define ID3V2_SetArtist(i,s,t) ID3V2_SetTextFrame(i, 'TPE1', s, t)
#define ID3V2_SetYear(i,s,t)   ID3V2_SetTextFrame(i, 'TYER', s, t)
#define ID3V2_SetTrack(i,s,t)  ID3V2_SetTextFrame(i, 'TRCK', s, t)
#define ID3V2_SetCD(i,s,t)     ID3V2_SetTextFrame(i, 'TPOS', s, t)

int ID3V2_SetTextFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int size, char *utf8text);

int ID3V2_GetPictureFrame(ID3V2 *id3v2, const unsigned char pictype, 
                          char **mimetype, char **description, void **picture, unsigned int *picsize);

int ID3V2_SetPictureFrame(ID3V2 *id3v2, const unsigned char pictype, 
                          const char *mimetype, const char *description,
                          void *picture, unsigned int picsize);
#endif



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

