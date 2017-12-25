#include <errno.h> 
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
#include <id3v2.h>
#include <id3v2frame.h>
#include <utfx.h>
#include <rawfile.h>
#include <printhex.h>
#include <stdbool.h>

#define VERSION "1.11.2" // --force230

int FixFrame(ID3V2 *id3v2, const unsigned int ID);
int CopyArgument(char **dst, char *src);
int ProcessSetArgument(ID3V2 *id3v2, const unsigned int ID, char *argument);
int ProcessGetArgument(ID3V2 *id3v2, const unsigned int ID, const char *name);
int ShowFramelist(ID3V2 *id3v2);
int DumpFrame(ID3V2 *id3v2, char *frameid);
void SafeFree(void* addr);
int ValidatePath(char **path, int accessmode); // makes path absolute and checks access accessmode: W_OK|R_OK


void PrintUsage()
{
    printf("\e[1;31mid3edit [\e[1;34m%s\e[1;31m]\e[0m\n", VERSION);
    printf("\n");
    printf("\e[1;37m id3edit \e[1;34m--help\n");
    printf("\e[1;37m id3edit \e[1;34m--version\n");
    printf("\e[1;37m id3edit \e[1;34moptions mp3file\n\n");

    // tag options
    printf("\e[1;34m Tag options:\n\e[1;37m");
    // setter
    printf("\t\e[1;46m  Option       \e[45m Arg. \e[44m  Description  \e[1;46m ID \e[45m  Example  \e[0m\n");
    printf("\t\e[1;36m --set-name    \e[35m name \e[34m Songname      \e[0;36mTIT2\e[35m Sonne    \n");
    printf("\t\e[1;36m --set-album   \e[35m name \e[34m Album name    \e[0;36mTALB\e[35m Mutter   \n");
    printf("\t\e[1;36m --set-artist  \e[35m name \e[34m Artist name   \e[0;36mTPE1\e[35m Rammstein\n");
    printf("\t\e[1;36m               \e[35m      \e[31m               \e[0;36mTPE2\e[35m          \n");
    printf("\t\e[1;36m --set-artwork \e[35m path \e[34m Artwork       \e[0;36mAPIC\e[35m ./pic.jpg\n");
    printf("\t\e[1;36m               \e[35m      \e[31m  !!  Just jpg supported! - NO CHECK\n");
    printf("\t\e[1;36m --set-release \e[35m year \e[34m Release year  \e[0;36mTYER\e[35m 2001     \n");
    printf("\t\e[1;36m               \e[35m      \e[31m              (\e[0;36mTDRC\e[1;31m) not implemented\n");
    printf("\t\e[1;36m --set-track   \e[35m track\e[34m Track number  \e[0;36mTRCK\e[35m 03/11    \n");
    printf("\t\e[1;36m --set-cd      \e[35m cd   \e[34m CD number     \e[0;36mTPOS\e[35m 1/1      \n");
    // getter
    printf("\t\e[1;36m --get-\e[35m$INFO         \e[34m Show \e[35m$INFO\e[34m={"
                                                                    "\e[0;35mname\e[1;34m,"
                                                                    "\e[0;35malbum\e[1;34m,"
                                                                    "\e[0;35martist\e[1;34m,"
                                                                    "\e[0;35mrelease\e[1;34m,"
                                                                    "\e[0;35mtrack\e[1;34m,"
                                                                    "\e[0;35mcd\e[1;34m}\n");
    printf("\t\e[1;36m --get-all     \e[35m      \e[34m Show all Tags      \n");
    printf("\t\e[1;36m --get-framelist\e[35m     \e[34m Show the framelist \n");
    printf("\n");
     // (TDRC für das jahr ??? lt mutagenx)

    // Other options
    printf("\e[1;34m Other options:\n\e[1;37m");
    printf("\t\e[1;46m  Option       \e[45m Arg. \e[44m  Description      \e[1;45m  Example  \e[0m\n");
    printf("\t\e[1;36m --outfile     \e[35m path \e[34m path to mp3       \e[0;35m ./new.mp3\n");
    printf("\t\e[1;36m --dump        \e[35m ID   \e[34m Hexdump of a tag  \e[0;35m TXXX     \n");
    printf("\n");

    // Flags
    printf("\e[1;34m Other options:\n\e[1;37m");
    printf("\t\e[1;46m  Flag         \e[1;44m  Description         \e[0m\n");
    printf("\t\e[1;36m --readonly    \e[1;34m Do not Write to disk \n");
    printf("\t\e[1;36m --create      \e[1;34m Create ID3v2 Tag iff it\'s a bare mp3 file \n");
    printf("\t\e[1;36m --clear       \e[1;34m Remove all ID3v2 before adding new \n");
    printf("\t\e[1;36m --showheader  \e[1;34m Prints details of the headers while reading \n");
    printf("\t\e[1;36m --force230    \e[1;34m Force ID3 v 2.3.0 when writing \n");
    printf("\n");

    printf("\e[1;31m  * \e[1;33m\e[4mExperimental\e[0m\e[1;33m Software! - Do not do experiments with it!\e[0m\n");
    printf("\e[1;31m  * \e[1;33mArguments are \e[4mnot checked\e[0m\e[1;33m if they are valid (except pathes)!\e[0m\n");
    printf("\e[1;31m  * \e[1;37mAll \"Text Information Frames\" set will be \e[4mUTF-16 encoded\e[0m\e[1;37m.\e[0m\n");
}

int main(int argc, char *argv[])
{
    int exitcode = 1; // will be set to zero as last task - so all goto exit lead in returning -1

    // parse arguments
    if(argc <= 1)
    {
        PrintUsage();
        exit(0);
    }
    if(argc == 2) // maybe something special
    {
        if((strncmp("--help", argv[1], 20) == 0) || (strncmp("-h", argv[1], 20) == 0))
        {
            PrintUsage();
            exit(0);
        }
        else if((strncmp("--version", argv[1], 20) == 0) || (strncmp("-v", argv[1], 20) == 0))
        {
            printf("%s\n", VERSION);
            exit(0);
        }
        else
        {
            fprintf(stderr, "Invalid Argument - Input-path missing?\n");
            PrintUsage();
            exit(-1);
        }
    }

    char *newname   = NULL;
    char *newalbum  = NULL;
    char *newartist = NULL;
    char *newartwork= NULL;
    char *newrelease= NULL;
    char *newtracknr= NULL;
    char *newcdnr   = NULL;
    char *dumpframe = NULL;
    char *mp3path   = NULL; // path to input file
    char *altpath   = NULL; // path to output file (if NULL, input = output)
    bool readonly   = false;
    bool createtag  = false;
    bool cleartags  = false;
    bool force230   = false;
    bool getframelist=false;
    bool getname    = false;
    bool getalbum   = false;
    bool getartist  = false;
    bool getrelease = false;
    bool gettracknr = false;
    bool getcdnr    = false;
    bool getall     = false;

    // start with agrv[1], the first argument (argv[0] is the programm file)
    // end one argument befor the end because the last one is the mp3-file
    int argi;
    for(argi=1; argi<argc-1; argi++)
    {
        // check for options without argument
#define GETFLAG(v,n) if(strncmp((n), argv[argi], 20) == 0){(v) = true; continue;}
        GETFLAG(readonly,     "--readonly")
        GETFLAG(createtag,    "--create")
        GETFLAG(cleartags,    "--clear")
        GETFLAG(force230,     "--force230")
        GETFLAG(OPT_PrintHeader, "--showheader")    // Global flag for the id3v2.c code
        GETFLAG(getframelist, "--get-framelist")
        GETFLAG(getall,       "--get-all")
        GETFLAG(getname,      "--get-name")
        GETFLAG(getalbum,     "--get-album")
        GETFLAG(getartist,    "--get-artist")
        GETFLAG(getrelease,   "--get-release")
        GETFLAG(gettracknr,   "--get-track")
        GETFLAG(getcdnr,      "--get-cd")
 
        // check for options with argument
#define GETARG(v,n) if((v) == NULL && strncmp((n), argv[argi], 20) == 0) \
                    {CopyArgument(&(v), argv[++argi]); continue;}
        GETARG(newname,    "--set-name")
        GETARG(newalbum,   "--set-album")
        GETARG(newartist,  "--set-artist")
        GETARG(newartwork, "--set-artwork")
        GETARG(newrelease, "--set-release")
        GETARG(newtracknr, "--set-track")
        GETARG(newcdnr,    "--set-cd")
        GETARG(altpath,    "--outfile")
        GETARG(dumpframe,  "--dump")
        
        // invalid option
        fprintf(stderr, "Invalid Argument: \"%20s\"\n", argv[argi]);
        PrintUsage();
        goto exit;
    }

    if(argi > argc-1)
    {
        fprintf(stderr, "Missing input mp3file!\n");
        PrintUsage();
        goto exit;
    }

    // Now get the last argument - this shall be the path to the mp3 file
    CopyArgument(&mp3path, argv[argc-1]);

    // Convert relative paths to absolute paths and check access
    if(ValidatePath(&mp3path,    W_OK|R_OK) != 0) goto exit;
    if(ValidatePath(&newartwork,      R_OK) != 0) goto exit;

    // OPEN
    int error;
    ID3V2 *id3v2 = NULL;
    error = ID3V2_Open(&id3v2, mp3path, createtag);
    if(error)
    {
        fprintf(stderr, "ID3V2_Open failed with error %i!\n", error);
        goto exit;
    }

    // Process programm arguments
    if(getframelist) if(ShowFramelist(id3v2)        != 0) goto exit;
    if(dumpframe)    if(DumpFrame(id3v2, dumpframe) != 0) goto exit;

    // Get Tags
#define PROCESSGETARGUMENT(a,i,n)  if(getall || (a)) if(ProcessGetArgument(id3v2, (i), (n)) != 0) goto exit;
    if(getall
     ||getname
     ||getalbum
     ||getartist
     ||getrelease
     ||gettracknr
     ||getcdnr) printf("\e[1;46m  ID  \e[44m  Name    \e[46m  Value                 \e[0m\n");
    PROCESSGETARGUMENT(getname,    'TIT2', "\e[0;36m TIT2 \e[1;34m Name:     \e[36m")
    PROCESSGETARGUMENT(getalbum,   'TALB', "\e[0;36m TALB \e[1;34m Album:    \e[36m")
    PROCESSGETARGUMENT(getartist,  'TPE1', "\e[0;36m TPE1 \e[1;34m Artist:   \e[36m")
    PROCESSGETARGUMENT(getartist,  'TPE2', "\e[0;36m TPE2 \e[1;34m           \e[36m")
    PROCESSGETARGUMENT(getrelease, 'TYER', "\e[0;36m TYER \e[1;34m Release:  \e[36m")
    PROCESSGETARGUMENT(gettracknr, 'TRCK', "\e[0;36m TRCK \e[1;34m Track:    \e[36m")
    PROCESSGETARGUMENT(getcdnr,    'TPOS', "\e[0;36m TPOS \e[1;34m CD:       \e[36m")

    // Process some more flags
    if(cleartags) ID3V2_RemoveAllFrames(id3v2);

    // Set Tags
    if(ProcessSetArgument(id3v2, 'TIT2', newname)    != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'TALB', newalbum)   != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'TPE1', newartist)  != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'TPE2', newartist)  != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'TYER', newrelease) != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'TRCK', newtracknr) != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'TPOS', newcdnr)    != 0) goto exit;
    if(ProcessSetArgument(id3v2, 'APIC', newartwork) != 0) goto exit;

    // CLOSE
    if(readonly)
    {
        SafeFree(altpath);
        altpath = "/dev/null";  // if ID3V2_Closes sees /dev/null, nothing will be stored
    }

    // Force ID3 version 2.3.0
    if(force230) id3v2->header.version_major = 3;

    error = ID3V2_Close(id3v2, altpath);
    if(error)
    {
        fprintf(stderr, "ID3V2_Close failed with error %i!\n", error);
        goto exit;
    }
    // now the exit is wanted and not because of an occured error
    exitcode = 0;
    
exit:

    SafeFree(newname);
    SafeFree(newalbum);
    SafeFree(newartist);
    SafeFree(newartwork);
    SafeFree(newrelease);
    SafeFree(newtracknr);
    SafeFree(newcdnr);
    SafeFree(mp3path);
    return exitcode;
}

//////////////////////////////////////////////////////////////////////////////

int FixFrame(ID3V2 *id3v2, const unsigned int ID)
{
    unsigned int size;
    char *data;
    int error;

    // READ
    error = ID3V2_GetTextFrame(id3v2, ID, &size, &data);
    if(error == ID3V2ERROR_FRAMENOTFOUND)
        return 0;   // do not fix frames that doesn't exist
    if(error)
        return error;
    printf("\e[1;34mFixing \"%s\"\e[0m\n", data);

    // WRITE
    error = ID3V2_SetTextFrame(id3v2, ID, size, data);
    if(error)
    {
        SafeFree(data);
        return error;
    }

    SafeFree(data);
    return 0;
}

//////////////////////////////////////////////////////////////////////////////

int ProcessSetArgument(ID3V2 *id3v2, const unsigned int ID, char *argument)
{
    if(argument != NULL)
    {
        int error;
        switch(ID)
        {
            case 'TYER': // The 'Year' frame is a numeric string. It is always four characters long.
            case 'TRCK': // E.g. "4/9"
            case 'TPOS': // E.g. "1/2"
            case 'TIT2':
            case 'TALB':
            case 'TPE1':
            case 'TPE2':
                {
                    error = ID3V2_SetTextFrame(id3v2, ID, strlen(argument), argument);
                    if(error)
                    {
                        fprintf(stderr, "ID3V2_SetTextFrame for ID 0x%08X failed with error %i!\n", ID, error);
                        return -1;
                    }
                    break;
                }

            case 'APIC':
                {
                    void *picture = NULL;
                    unsigned int picsize;
                    error = RAWFILE_Read(argument, &picture, &picsize);
                    if(error)
                    {
                        fprintf(stderr, "RAWFILE_Read failed for \"%s\" with error %i!\n", argument, error);
                        return -1;
                    }

                    error = ID3V2_SetPictureFrame(id3v2, 0x03 /*front cover*/, 
                                                  "image/jpg", NULL, picture, picsize);
                    SafeFree(picture);
                    if(error)
                    {
                        fprintf(stderr, "ID3V2_SetPictureFrame failed with error %i!\n", error);
                        return -1;
                    }

                    break;
                }

            default:
                {
                        fprintf(stderr, "ID not supported as argument! (0x%08X)\n", ID);
                        return -1;
                }
        }
    }

    return 0;
}

//----------------------------------------------------------------------------

int ProcessGetArgument(ID3V2 *id3v2, const unsigned int ID, const char *name)
{
    int error;
    unsigned int size;
    char *text = NULL;
    switch(ID)
    {
        case 'TYER': // The 'Year' frame is a numeric string. It is always four characters long.
        case 'TRCK': // E.g. "4/9"
        case 'TPOS': // E.g. "1/2"
        case 'TIT2':
        case 'TALB':
        case 'TPE1':
        case 'TPE2':
            {
                printf("%s", name);
                error = ID3V2_GetTextFrame(id3v2, ID, &size, &text);
                if(error == ID3V2ERROR_FRAMENOTFOUND)
                {
                    printf("\e[0;31mFrame does not Exist\e[0m\n");
                }
                else if(error)
                {
                    fprintf(stderr, "ID3V2_SetTextFrame for ID 0x%08X failed with error %i!\n", ID, error);
                    return -1;
                }
                else
                {
                    printf("%s\e[0m\n", text);
                    SafeFree(text);
                }
                break;
            }

        default:
            {
                    fprintf(stderr, "ID not supported as argument! (0x%08X)\n", ID);
                    return -1;
            }
    }

    return 0;
}

//----------------------------------------------------------------------------

int ShowFramelist(ID3V2 *id3v2)
{
    // Headline
    printf("\e[1;37m");
    printf("\e[46m ID \e[44m  Size  \e[44m  Flags  \e[44m Encoding                      \e[0m\n");

    // start printing frames
    ID3V2_FRAME *frame;
    frame = id3v2->framelist;
    while(frame)
    {
        // print ID - color shall indicate if supported or not
        switch(frame->ID)
        {
            case 'APIC':
            case 'TYER':
            case 'TRCK':
            case 'TPOS':
            case 'TIT2':
            case 'TALB':
            case 'TPE1':
            case 'TPE2':
                printf("\e[1;36m"); // supported
                break;

            default:
                printf("\e[1;31m"); // not supported
                break;
        }
        printf("%c%c%c%c", ID3V2ID_TO_CHARS(frame->ID));

        // size
        printf("\e[1;34m %6i ", frame->size);

        // flags (flags are not supported now, if there are flags, print them red
        printf("%s 0x%04X ", (frame->flags == 0x0000)?"\e[1;34m":"\e[1;31m", frame->flags);

        // if frame is a text-frame, get some more infos - also for APIC
        unsigned char *data = (unsigned char*)frame->data;
        data = (unsigned char*)frame->data;
        if((frame->ID >> 24) == 'T')
        {
            // encoding
            unsigned char encoding;
            encoding = data[0];
            if(encoding == 0x00) // ISO 8859-1
                printf("\e[1;30m ISO 8859-1 ");
            else if(encoding == 0x01)
                printf("\e[1;34m UTF-16 "); // 4 byte space for byteorder ("LE  ", "BE  ")
            else
                printf("\e[1;31m Invalid!   ");

            // BOM if UTF-16
            if(encoding == 0x01)
            {
                unsigned short *utf16data = (unsigned short*)&data[1];
                unsigned short byteorder;
                utf16data = (unsigned short*)&data[1];
                byteorder = utf16data[0];
                if(byteorder == UTF16BOM_BE)
                    printf("\e[0;36mBE  ");
                else if(byteorder == UTF16BOM_LE)
                    printf("\e[0;36mLE  ");
                else
                    printf("\e[1;31mBOM missing ");

                // now check if there are more BOMs (caused by this fucking tool I used before)
                if(utf16data[1] == UTF16BOM_BE || utf16data[1] == UTF16BOM_LE)
                    printf("\e[1;33mMultiple BOM found! ");
            }
        }
        else if(frame->ID == 'APIC')
        {
            char *mimetype;
            mimetype = (char*)(data + 1); // regarding to the specification this is a 0-terminated ISO 8859-1 string
            if(strncmp(mimetype, "image/jpg", 10) == 0)
                printf("\e[1;34m ");
            else if(strncmp(mimetype, "image/jpeg", 10) == 0)
                printf("\e[1;34m ");
            else
                printf("\e[1;31m ");
            printf("%-15s ", mimetype);
        }

        printf("\e[0m\n");

        // get next frame
        frame = (ID3V2_FRAME*)frame->next;
    }
    return 0;
}

//----------------------------------------------------------------------------

int DumpFrame(ID3V2 *id3v2, char *frameid)
{
    ID3V2_FRAME *frame;
    unsigned int ID = be32toh(*(unsigned int*)frameid);
    frame = id3v2->framelist;
    while(frame)
    {
        if(frame->ID == ID)
        {
            // Meta-data:
            printf("\e[1;34mID: \e[1;36m%c%c%c%c ", ID3V2ID_TO_CHARS(frame->ID));
            printf("\e[1;34m, Size: \e[0;36m%6i ", frame->size);
            printf("\e[1;34m, Flags: \e[0;36m0x%04X\e[0m\n", frame->flags);

            unsigned char *data = (unsigned char*)frame->data;
            data = (unsigned char*)frame->data;
            if((frame->ID >> 24) == 'T')
            {
                // encoding
                unsigned char encoding;
                encoding = data[0];

                printhex(frame->data, (frame->size > 0x100)?0x100:frame->size, 16, 
                        0, "\e[1;36m",          // encoding
                        1, (encoding==0x01)?"\e[1;35m":"\e[1;34m",  // BOM
                        3, "\e[1;34m", -1);
            }
            else
            {
                printhex(frame->data, (frame->size > 0x100)?0x100:frame->size, 16, 
                        0, "\e[1;34m", -1);
            }
            if(frame->size > 0x100)
                printf("\e[0;33mThere are more bytes…");
            printf("\n\e[0m");
        }

        frame = (ID3V2_FRAME*)frame->next;
    }

    return 0;
}

//////////////////////////////////////////////////////////////////////////////

int CopyArgument(char **dst, char *src)
{
    // Do nothing if we don't have a destination
    if(dst == NULL)
        return 0;

    // check if this argument is already in use
    if(*dst != NULL)
        return -1;

    int length = strlen(src);
    *dst = malloc(sizeof(char)*length+1); // +1 for the \0
    if(*dst == NULL)
    {
        fprintf(stderr, "Critical Error: malloc returned NULL!\n");
        return -1;
    }

    strncpy(*dst, src, length);
    return 0;
}

void SafeFree(void* addr)
{
    if(addr != NULL)
        free(addr);
}

int ValidatePath(char **path, int accessmode) // accessmode: W_OK|R_OK
{
    if(path == NULL)
        return 0;
    if(*path== NULL)
        return 0;

    // Convert relative paths to absolute paths
    char *retval = realpath(*path, NULL);
    if(retval == NULL)
    {
        fprintf(stderr, "Converting \"%s\" to a real path failed with error \"%s\"\n", *path, strerror(errno));
        return -1;
    }
    free(*path);
    *path = retval;

    // Check path
    if(access(*path, accessmode) == -1)
    {
        fprintf(stderr, "File %s does not exist or does not have R and/or W permissions!\n", *path);
        return -1;
    }

    return 0;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

