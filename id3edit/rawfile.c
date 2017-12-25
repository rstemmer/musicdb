#include <errno.h> 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <endian.h>
#include <rawfile.h>

#ifdef DEBUG
#include <printhex.h>
#endif

int RAWFILE_Read(const char *path,  void **rawdata, unsigned int *size)
{
    FILE *file;
    // open file
    file = fopen(path, "rb");
    if(file == NULL)
    {
        fprintf(stderr, "Opening \"%s\" failed with error \"%s\"\n", path, strerror(errno));
        return RAWFILEERROR_PATHERROR;
    }

    // get size
    unsigned int filesize;
    fseek(file, 0, SEEK_END); // go to the end of file
    filesize  =  ftell(file); // get position in file
    fseek(file, 0, SEEK_SET); // go to the begin of file

    // allocate memory
    unsigned char *data;
    data = malloc(filesize);
    if(data == NULL)
    {
        fprintf(stderr, "Fatal Error! - malloc returned NULL!\n");
        return RAWFILEERROR_FATAL;
    }

    // read data
    fread(data, 1, filesize, file);

    // close file
    fclose(file);
    file = NULL;

    // return everything
    if(rawdata)
        *rawdata = data;
    if(size)
        *size = filesize;

    return RAWFILEERROR_NOERROR;
}

//////////////////////////////////////////////////////////////////////////////

int RAWFILE_Write(const char *path, void  *rawdata, unsigned int size)
{
    FILE *file;
    // open file
    file = fopen(path, "wb");
    if(file == NULL)
    {
        fprintf(stderr, "Opening \"%s\" failed with error \"%s\"\n", path, strerror(errno));
        return RAWFILEERROR_PATHERROR;
    }

    // read data
    fwrite(rawdata, 1, size, file);

    // close file
    fclose(file);

    return RAWFILEERROR_NOERROR;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

