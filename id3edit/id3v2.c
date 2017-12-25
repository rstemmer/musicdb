#include <errno.h> 
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
#include <id3v2.h>
#include <endian.h>
#include <stdbool.h>

bool OPT_PrintHeader = false;

unsigned int ID3V2_EncodeSize(unsigned int size)
{
    // 1.: 0000xxxxxxxxxxxxxxxxxxxxxxxxxxxx
    //  -> 0xxxxxxx0xxxxxxx0xxxxxxx0xxxxxxx
    unsigned int byte = 0;
    unsigned int tmp  = 0;
    for(int i=0; i<4; i++)
    {
        byte  = size >> (i*7);
        byte &= 0x7F;
        tmp  |= byte << (i*8);
    }

    // 2.: LE -> BE
    unsigned int encsize;
    encsize = htobe32(tmp);

    return encsize;
}
unsigned int ID3V2_DecodeSize(unsigned int encsize)
{
    // 1.: BE -> LE
    unsigned int tmp;
    tmp = be32toh(encsize);

    // 2.: 0xxxxxxx0xxxxxxx0xxxxxxx0xxxxxxx
    //  -> 0000xxxxxxxxxxxxxxxxxxxxxxxxxxxx
    unsigned int byte = 0;
    unsigned int size = 0;
    for(int i=0; i<4; i++)
    {
        byte  = tmp  >> (i*8);
        byte &= 0x7F;
        size |= byte << (i*7);
    }

    return size;
}

int ID3V2_Open(ID3V2 **id3v2, const char *path, bool createtag)
{
    unsigned int bigendian;
    *id3v2 = NULL; // no undefined state please - the new struct gets assigned to id3v2 at the end, if everything if fine

    // Create main structure
    ID3V2 *id3 = (ID3V2*) malloc(sizeof(ID3V2));
    if(id3 == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned 0!\n");
        return ID3V2ERROR_FATAL;
    }

    // Copy path
    int pathlength = strlen(path) + 1;  // don't forget the terminating \0
    id3->path = (char*) malloc(sizeof(char)*pathlength);
    if(id3->path == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned 0!\n");
        free(id3);
        return ID3V2ERROR_FATAL;
    }

    strncpy(id3->path, path, pathlength);

    // Open file
    id3->file = fopen(path, "rb");
    if(id3->file == NULL)
    {
        fprintf(stderr, "Opening \"%s\" failed with error \"%s\"\n", path, strerror(errno));
        free(id3->path);
        free(id3);
        return ID3V2ERROR_PATHERROR;
    }

    // Read Header
    fread(&id3->header.ID,              1, 3, id3->file);
    fread(&id3->header.version_major,   1, 1, id3->file);
    fread(&id3->header.version_minor,   1, 1, id3->file);
    fread(&id3->header.flags,           1, 1, id3->file);

    // the headersize is stored as big endian. This must be converted to little endian.
    // beside this, it has 7 bit per byte...
    unsigned int encsize; 
    fread(&encsize, 4, 1, id3->file);
    id3->header.origsize = ID3V2_DecodeSize(encsize);
    id3->header.realsize = 0;   // initialize with zero. From now, every byte read this will be incremented

    // print the header if set in the options, or if debugging is enabled
#ifndef DEBUG
    if(OPT_PrintHeader)
#endif
    {
        printf("\e[1;37mHeader\n");
        printf("\e[1;34mID:      \033[0;36m\'%c%c%c\'\n", id3->header.ID[0], id3->header.ID[1], id3->header.ID[2]);
        printf("\e[1;34mVersion: \033[0;36m2.%i.%i\n",    id3->header.version_major, id3->header.version_minor);
        printf("\e[1;34mFlags:   \033[0;36m0x%02X\n",     id3->header.flags);
        printf("\e[1;34mSize:    \033[0;36m%i\n",         id3->header.origsize);
        if(createtag)
            printf("\e[1;30m\tCreating new Tag if 0x%02X == 0xFF && 0x%02X ∈ {0xFD,0xFB,0xFA,0xF3}\n", id3->header.ID[0], id3->header.ID[1]);
    }
    //printf("\e[0m0x%08X -> %08X\n", bigendian, id3->header.size);

    // check if I support this ID3 thing. If not, create one if allowad
    if(id3->header.ID[0] != 'I' || id3->header.ID[1] != 'D' || id3->header.ID[2] != '3')
    {
        // in case this is a bare mp3 file, just create a new tag
        if( (createtag && id3->header.ID[0] == 0xFF && id3->header.ID[1] == 0xFB)   // *.mp3 (standard)
         || (createtag && id3->header.ID[0] == 0xFF && id3->header.ID[1] == 0xFA)   // *.mp3 (found somewhere)
         || (createtag && id3->header.ID[0] == 0xFF && id3->header.ID[1] == 0xF3)   // *.mp3 (found somewhere)
         || (createtag && id3->header.ID[0] == 0xFF && id3->header.ID[1] == 0xFD) ) // *.mp3 (found somewhere)
        {
            id3->header.ID[0]         = 'I';
            id3->header.ID[1]         = 'D';
            id3->header.ID[2]         = '3';
            id3->header.version_major = 3;  // \_ version 2.3.0
            id3->header.version_minor = 0;  // /
            id3->header.flags         = 0;  // No flags
            id3->header.origsize      = 0;  // No frames
            // Reverse previous attempts to read the ID3 header
            fseek(id3->file, 0, SEEK_SET);  
        }
        else
        {
            fprintf(stderr, "ID: \'%c%c%c\' (%02X%02X%02X) not supported!\n", id3->header.ID[0], 
                                                                              id3->header.ID[1], 
                                                                              id3->header.ID[2],
                                                                              id3->header.ID[0], 
                                                                              id3->header.ID[1], 
                                                                              id3->header.ID[2]);
            free(id3->path);
            free(id3);
            return ID3V2ERROR_NOTSUPPORTED;
        }
    }
    if(id3->header.flags != 0)
    {
        fprintf(stderr, "Unsupported flags detected. Set flags are: 0x%02X\n", id3->header.flags);
        free(id3->path);
        free(id3);
        return ID3V2ERROR_NOTSUPPORTED;
    }
    if(id3->header.version_major == 4 && id3->header.version_minor == 0)
    {
        fprintf(stderr, "\e[1;33mWARNING:\e[0m ID3 Version 2.4.0 just partially supported and mostly untested!\n");
    }
    else if(id3->header.version_major != 3 || id3->header.version_minor != 0)
    {
        fprintf(stderr, "Version 2.%i.%i not supported yet! (just 2.3.0 allowed)\n",
                id3->header.version_major, 
                id3->header.version_minor);
        free(id3->path);
        free(id3);
        return ID3V2ERROR_NOTSUPPORTED;
    }

    // read extended header if available
    if(id3->header.flags & ID3V2HEADERFLAG_EXTENDEDHEADER)
    {
        fprintf(stderr, "Extended header are not supported yet!\n");
        free(id3->path);
        free(id3);
        return ID3V2ERROR_NOTSUPPORTED;
        // TODO
        /*
        fread(&bigendian, 4, 1, id3->file); id3->extheader.size        = be32toh(bigendian);
        fread(&bigendian, 2, 1, id3->file); id3->extheader.flags       = be16toh(bigendian);
        fread(&bigendian, 4, 1, id3->file); id3->extheader.paddingsize = be32toh(bigendian);
#ifndef DEBUG
        if(OPT_PrintHeader)
#endif
        {
            printf("\e[1;37mExtended Header\n");
            printf("\e[1;34mSize:         \033[0;36m%i\n",     id3->extheader.size);
            printf("\e[1;34mFlags:        \033[0;36m0x%04X\n", id3->extheader.flags);
            printf("\e[1;34mPadding Size: \033[0;36m%i\n",     id3->extheader.paddingsize);
        }
        */
    }
    else
    {
        id3->extheader.size        = 0;
        id3->extheader.flags       = 0;
        id3->extheader.paddingsize = 0;
    } 

    // read all frames
    id3->framelist = NULL;
    ID3V2_FRAME **next = &id3->framelist;
    unsigned int offset = 0;
    while(offset < id3->header.origsize)
    {
        ID3V2_FRAME *frame;
        // Allocate memory
        frame = (ID3V2_FRAME*) malloc(sizeof(ID3V2_FRAME));
        if(frame == NULL)
        {
            fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
            return ID3V2ERROR_FATAL;
        }

        // read meta data
        fread(&bigendian, 4, 1, id3->file); frame->ID    = be32toh(bigendian);
        if(frame->ID == 0x00000000) // we are in the padding area, end of ID3 reached
        {
            free(frame); // no need for this frame
            offset += 4; // 4 bytes of the padding bytes already read
            break;       // this is the end of the list, reading completed
        }
        fread(&bigendian, 4, 1, id3->file); frame->size  = be32toh(bigendian);
        fread(&bigendian, 2, 1, id3->file); frame->flags = be16toh(bigendian);

        // read data
        frame->data = malloc(frame->size);
        if(frame->data == NULL)
        {
            fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
            return ID3V2ERROR_FATAL;
        }
        fread(frame->data, 1, frame->size, id3->file);

#ifndef DEBUG
        if(OPT_PrintHeader)
#endif
        {
            printf("\e[1;37mFrame\e[0m @ offset %6i: ", offset);
            printf("\e[1;34mID: \033[0;36m\'%c%c%c%c\'", (frame->ID >> 24) & 0xFF,
                                                         (frame->ID >> 16) & 0xFF,
                                                         (frame->ID >>  8) & 0xFF,
                                                         (frame->ID >>  0) & 0xFF);
            printf("\e[1;34m, Flags: \033[0;36m0x%04X",   frame->flags);
            printf("\e[1;34m, Size: \033[0;36m%6i\n",     frame->size);
        }

        /*
        // Put frame into list (this reverses the order of the tags in the file)
        frame->next = id3->framelist;
        id3->framelist = frame;
        */
        *next = frame;
        next  = &frame->next;

        // trace offset and real size separately, they can be different due to padding
        offset               += frame->size + 10; // 10: size of the frame header
        id3->header.realsize += frame->size + 10; // 10: size of the frame header
    }
    *next = NULL; // End of list

    // Reading done
    *id3v2 = id3;
#ifndef DEBUG
    if(OPT_PrintHeader)
#endif
    {
        printf("\e[1;33mAdjusting header size: ");
        printf("\e[1;34mOrig. size: \e[1;36m%i\e[1;34m, real size: \e[1;36m%i\e[0m\n", id3->header.origsize,
                                                                                       id3->header.realsize);
    }

    // PEDANTIC HEADER CHECK
    // check if the padding-bytes are realy padding bytes or if the headers size value is wrong (may happen with bad mp3 files)
    int data;
    while(offset < id3->header.origsize)
    {
        // Get padding byte
        if((data = getc(id3->file)) == EOF)
            return ID3V2ERROR_UNEXPECTEDEOF;

        // Check if valid, if not, try to rescue the file by assuming that the headers size value is invalid
        if((char)data != 0x00)
        {
            fprintf(stderr, "\e[1;31mBad padding byte found at offset %i (file pos. %li) - expected at offset %i.\n", 
                    offset, ftell(id3->file) - 1, id3->header.origsize);
            fprintf(stderr, "\tInvalid byte: 0x%X\n", ((unsigned)data)&0x00FF);
            fprintf(stderr, "\tI\'ll try to fix it.  If it doesn\'t work, nothing will become worse.\n");
            //id3->header.origsize = id3->header.realsize;
            id3->header.origsize = offset; // where the padding end

            // get a valid state in case the padding-check failed - +10 for the ID3 main header size
            fseek(id3->file, id3->header.origsize + 10, SEEK_SET);  
            break;
        }
        offset++;
    }

    // Now, the magic mp3-ID shall come
    unsigned short magicword;
    fread(&magicword, 2, 1, id3->file);
    if(magicword != 0xFAFF 
    && magicword != 0xFBFF 
    && magicword != 0xFDFF
    && magicword != 0xF3FF) // keep LE in mind
    {
        fprintf(stderr, "\e[1;31mMagic mp3-ID not found at expected offset %i (file pos. %li)!\n", 
                offset, ftell(id3->file) - 1);
        fprintf(stderr, "\tInvalid ID: 0x%4X\n", magicword&0x0FFFF);
        fprintf(stderr, "\tAt file pos. %li\n", ftell(id3->file));
        fprintf(stderr, "\tI\'ll do nothing - nothing will become worse.\n");
    }

    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_Close(ID3V2 *id3v2, const char *altpath)
{
    ID3V2 *id3 = id3v2; // two lettes less... well, internally I use id3 so this make the code more comfortable
    int error;
    bool readonly = false;

    if(altpath != NULL)
    {
        // check if altpath is /dev/null - this means readonly-mode
        if(strncmp("/dev/null", altpath, 10) == 0)
        {
            readonly = true;
        }
        // check if altpath is the same as the orig one. If yes, do not use the altpath, use a tmpfile instead
        else if(strncmp(id3v2->path, altpath, strlen(id3v2->path)) == 0)
        {
            altpath = NULL; // use a tempfile to avoid problems like infinit copy
        }
    }

    // open secound (destination) file. If altpath is given, this one is used, otherwise a temporary one
    FILE *dstfile = NULL;
    if(altpath == NULL) // open tmp file
    {
        // create temporary file
        dstfile = tmpfile();
        if(dstfile == NULL)
        {
            fprintf(stderr, "Creating tmp file failed with error \"%s\"\n", strerror(errno));
            return ID3V2ERROR_PATHERROR;
        }
    }
    else if(readonly == false)
    {
        dstfile = fopen(altpath, "w+b");
        if(dstfile == NULL)
        {
            fprintf(stderr, "Opening file \"%s\" failed with error \"%s\"\n", altpath, strerror(errno));
            return ID3V2ERROR_PATHERROR;
        }
    }
#ifdef DEBUG
    printf("\e[1;37mClosing...\n");
    printf("\e[1;34mReadonly: \e[1;36m%s\n", readonly?"true":"false");
    printf("\e[1;34mAltpath:  \e[1;36m%s\n", altpath?altpath:"\e[0;36mNULL");
#endif

    // Store header
    if(!readonly)
    {
        fwrite(&id3->header.ID,            1, 3, dstfile); //\. 
        fwrite(&id3->header.version_major, 1, 1, dstfile); // \_ these values are always valid
        fwrite(&id3->header.version_minor, 1, 1, dstfile); // /
        fwrite(&id3->header.flags,         1, 1, dstfile); /// 

        // encode size to 7bit/byte BE
        // IMPORTANT: I use real size and my own padding bytes
        unsigned int encsize; 
        encsize = ID3V2_EncodeSize(id3->header.realsize + ID3V2PADDING);
        fwrite(&encsize, 4, 1, dstfile);
    }

    // Drop extended header
    
    // Write frames
    ID3V2_FRAME *frame = id3->framelist;
    while(frame != NULL)
    {
        unsigned int bigendian;
        // store frame
        if(!readonly)
        {
#ifdef DEBUG
            printf("\e[1;33mWriting… ");
#endif
            bigendian = htobe32(frame->ID);    fwrite(&bigendian, 4, 1, dstfile);
            bigendian = htobe32(frame->size);  fwrite(&bigendian, 4, 1, dstfile);
            bigendian = htobe16(frame->flags); fwrite(&bigendian, 2, 1, dstfile);
        
            fwrite(frame->data, 1, frame->size, dstfile);
        }
#ifdef DEBUG
        printf("\e[1;37mStored frame: ");
        printf("\e[1;34mID: \033[1;36m\'%c%c%c%c\'", (frame->ID >> 24) & 0xFF,
                                                     (frame->ID >> 16) & 0xFF,
                                                     (frame->ID >>  8) & 0xFF,
                                                     (frame->ID >>  0) & 0xFF);
        printf("\e[1;34m, Flags: \e[1;36m0x%04X",     frame->flags);
        printf("\e[1;34m, Size: \e[1;36m%6i\e[0m\n",  frame->size);
#endif

        // select next frame
        ID3V2_FRAME *oldframe;
        oldframe = frame;
        frame    = frame->next;

        // free memory of old one
        free(oldframe->data);
        free(oldframe);
    }

    // write padding bytes
    if(!readonly)
    {
        for(int i=0; i < ID3V2PADDING; i++)
            fputc(0x00, dstfile);

        // copy audio data to the new file
        // jump to the end of the ID3 infos in the orig file
        // the 10 is for the main header, old/orig size is used because the source has the orig structure
        fseek(id3->file, id3->header.origsize + 10, SEEK_SET);
        int data;
        while((data = getc(id3->file)) != EOF)
            fputc(data, dstfile);

        // if a tmp file was used, replace the source file with new content
        if(altpath == NULL)
        {
            id3->file = freopen(id3->path, "w+b", id3->file); // reopen with write permission
            if(id3->file == NULL)
            {
                fprintf(stderr, "Re-opening file \"%s\" for write access failed with error \"%s\"\n", 
                        id3->path, strerror(errno));
                return ID3V2ERROR_PATHERROR;
            }
#ifdef DEBUG
            printf("\e[1;33mCopy tmp file to destination \e[0;33m(%s)\e[1;33m…\n\e[0m", id3->path);
            printf("\t\e[1;34mPos. Temp.File: \e[1;36m%10i\n", ftell(dstfile));
            printf("\t\e[1;34mPos. Dest.File: \e[1;36m%10i\n\e[0m", ftell(id3->file));
#endif
            // go to start of both files
            error = fseek(dstfile,   0, SEEK_SET);
            if(error)
            {
                fprintf(stderr, "fseek for temp.file failed with error \"%s\"\n", strerror(errno));
                return ID3V2ERROR_WRITEERROR;
            }
            
            error = fseek(id3->file, 0, SEEK_SET);
            if(error)
            {
                fprintf(stderr, "fseek for dest.file failed with error \"%s\"\n", strerror(errno));
                return ID3V2ERROR_WRITEERROR;
            }

            // and copy from temporary file to destination file
            while((data = getc(dstfile)) != EOF)
            {
                if(fputc(data, id3->file) == EOF)
                {
                    fprintf(stderr, "Writing data from temporary file to destination failed\n");
                    return ID3V2ERROR_WRITEERROR;
                }
            }
#ifdef DEBUG
            printf("\e[1;32mdone\n\e[0m");
            printf("\t\e[1;34mPos. Temp.File: \e[1;36m%10i\n", ftell(dstfile));
            printf("\t\e[1;34mPos. Dest.File: \e[1;36m%10i\n\e[0m", ftell(id3->file));
#endif
        }
    }

    // close all files and free some memory
    if(dstfile != NULL)
        fclose(dstfile);
    fclose(id3->file);
    free(id3->path);
    free(id3);

    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

static ID3V2_FRAME *GetFrameById(ID3V2 *id3v2, const unsigned int ID)
{
    ID3V2_FRAME *frame;
    frame = id3v2->framelist;
    while(frame != NULL)
    {
        if(frame->ID == ID)
            return frame;

        frame = frame->next;
    }

    return NULL;
}

//----------------------------------------------------------------------------

static void ReplaceOrAppendFrameById(ID3V2 *id3v2, ID3V2_FRAME *newframe)
{
    ID3V2_FRAME *oldframe, *prevframe;
    if(newframe == NULL)
        return;
    
    id3v2->header.realsize += (newframe->size + 10); // add the size of the new frame to the sum of all frame size incl its header

    // Check if a complete new list must be created
    if(id3v2->framelist == NULL)
    {
        newframe->next = NULL;
        id3v2->framelist = newframe;
        return;
    }

    // Check if the first frame is the one
    if(id3v2->framelist->ID == newframe->ID)
    {
        oldframe         = id3v2->framelist;
        newframe->next   = oldframe->next;
        id3v2->framelist = newframe;
    }
    else
    {
        oldframe  = id3v2->framelist->next;
        prevframe = id3v2->framelist;
        while(oldframe != NULL)
        {
            if(oldframe->ID == newframe->ID)
            {
                newframe->next  = oldframe->next;
                prevframe->next = newframe; 
                break;
            }

            prevframe = oldframe;
            oldframe  = oldframe->next;
        }
    }

    if(oldframe != NULL)    // delete old one
    {
        id3v2->header.realsize -= (oldframe->size + 10); // sub the size of the old frame incl its header
        if(oldframe->data != NULL)
            free(oldframe->data);
        free(oldframe);
    }
    else                    // no old one? so the new one must be appended
    {
        newframe->next  = NULL;
        prevframe->next = newframe;
    }

    return;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_RemoveAllFrames(ID3V2 *id3v2)
{
    ID3V2_FRAME *nextframe, *oldframe;
    nextframe = id3v2->framelist;
    while(nextframe != NULL)
    {
        oldframe  = nextframe;
        nextframe = nextframe->next;

        id3v2->header.realsize -= (oldframe->size + 10); // sub size of data and header of the frame
        if(oldframe->data != NULL)
            free(oldframe->data);
        free(oldframe);
    }
    id3v2->framelist = NULL;
    return 0;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_GetFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int *size, void **data)
{
#ifdef DEBUG
        printf("\e[1;37mGet frame: ");
        printf("\e[1;34mID: \033[1;36m\'%c%c%c%c\'\n", (ID >> 24) & 0xFF,
                                                       (ID >> 16) & 0xFF,
                                                       (ID >>  8) & 0xFF,
                                                       (ID >>  0) & 0xFF);
#endif
    ID3V2_FRAME *frame;
    frame = GetFrameById(id3v2, ID);
    if(frame == NULL)
        return ID3V2ERROR_FRAMENOTFOUND;

    if(size != NULL)
        *size = frame->size;

    if(data != NULL)
    {
        *data = malloc(frame->size);
        if(*data == NULL)
        {
            fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
            return ID3V2ERROR_FATAL;
        }
        memcpy(*data, frame->data, frame->size);
    }

    return ID3V2ERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

int ID3V2_SetFrame(ID3V2 *id3v2, const unsigned int ID, unsigned int size, void *data)
{
#ifdef DEBUG
        printf("\e[1;37mSet frame: ");
        printf("\e[1;34mID: \033[1;36m\'%c%c%c%c\'\n", (ID >> 24) & 0xFF,
                                                       (ID >> 16) & 0xFF,
                                                       (ID >>  8) & 0xFF,
                                                       (ID >>  0) & 0xFF);
#endif
    // Allocate memory
    ID3V2_FRAME *frame;
    frame = malloc(sizeof(ID3V2_FRAME));
    if(frame == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }

    frame->data = malloc(size);
    if(frame->data == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return ID3V2ERROR_FATAL;
    }

    // Set values
    frame->ID   = ID;
    frame->flags= 0x0000;
    frame->size = size;
    memcpy(frame->data, data, size);

    // Replace (or append)
    ReplaceOrAppendFrameById(id3v2, frame);
    return ID3V2ERROR_NOERROR;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

