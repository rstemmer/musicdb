
function EncodePath(path)
{
    var escpath = "";
    var start = path.indexOf("/") + 1; // Filename starts behind the "/"
    escpath  = path.substr(0, start);
    escpath += encodeURIComponent(path.substr(start));
    return escpath;
}

function EncodeArtworkPath(imgpath, scaling)
{
    var start   = imgpath.lastIndexOf("/") + 1;
    var path    = imgpath.substr(0, start);
    var name    = imgpath.substr(start);
    var subdir  = "";
    if(scaling)
    {
        // Do not use a scaled default.jpg - they don't exist
        if(path != "default.jpg")
        {
            subdir  = scaling + "/";
        }
    }

    var encpath = encodeURI         ("artwork/" + subdir + path);
    var encname = encodeURIComponent(name);
    return encpath + encname;
}

function EncodeVideoThumbnailPath(framesdir, imgpath, width, height)
{
    if(width && height)
    {
        let scale  = ` (${width}×${height})`;
        let extpos = imgpath.lastIndexOf(".");
        let name   = imgpath.substr(0, extpos);
        let ext    = imgpath.substr(extpos);
        imgpath    = name + scale + ext;
    }

    let encpath = encodeURI         ("videoframes/" + framesdir + "/");
    let encname = encodeURIComponent(imgpath);
    return encpath + encname;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

