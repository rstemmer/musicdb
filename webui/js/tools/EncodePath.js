// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

function EncodePath(path)
{
    let start   = path.lastIndexOf("/") + 1; // File name starts behind the "/"
    let dirs    = path.substr(0, start);
    let name    = path.substr(start);
    let encdirs = encodeURI         (dirs);
    let encname = encodeURIComponent(name);
    return encdirs + encname;
}



function EncodeArtworkPath(imgpath, scaling)
{
    let start  = imgpath.lastIndexOf("/") + 1;
    let path   = imgpath.substr(0, start);
    let name   = imgpath.substr(start);
    let subdir = "";

    if(scaling)
    {
        // Do not use a scaled default.jpg - they don't exist
        if(name != "default.jpg")
        {
            subdir  = scaling + "/";
        }
    }

    let encpath = encodeURI         ("data/artwork/" + subdir + path);
    let encname = encodeURIComponent(name);
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

