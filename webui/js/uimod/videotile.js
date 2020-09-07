
"use strict";


class VideoTileDropZone extends DropTarget
{
    constructor(entryid)
    {
        super();
        this.element    = document.createElement("div");
        //this.element.id = "DropZone_" + position;
        this.element.classList.add("VideoQueueTile");
        this.element.classList.add("VideoTileDropZone");
        
        this.entryid    = entryid;

        this.BecomeDropTarget();
    }



    GetHTMLElement()
    {
        return this.element;
    }



    onTransfer(draggableid)
    {
        let draggable = document.getElementById(draggableid);
        let entryid   = draggable.dataset.entryid;
        let musictype = draggable.dataset.musictype;
        let musicid   = draggable.dataset.musicid;
        let droptask  = draggable.dataset.droptask;

        switch(droptask)
        {
            case "move":
                if(entryid == this.entryid)
                    break;

                if(musictype == "song")
                    MusicDB_Call("MoveSongInQueue", {entryid:entryid, afterid:this.entryid});
                else if(musictype == "video")
                    MusicDB_Call("MoveVideoInQueue", {entryid:entryid, afterid:this.entryid});
                break;
        }
        window.console && console.log(draggable.dataset);
    }
}

class VideoQueueTile extends Draggable
{
    constructor(MDBVideo, MDBArtist, entryid, position, buttonbox)
    {
        super();
        this.videoid     = MDBVideo.id;
        let videoname    = MDBVideo.name.replace(" - ", " – ");
        let videorelease = MDBVideo.release;
        let artistname   = MDBArtist.name;
        let artistid     = MDBArtist.id;

        this.element     = document.createElement("div");
        this.element.id  = entryid;
        this.element.dataset.entryid   = entryid;
        this.element.dataset.musictype = "video";
        this.element.dataset.musicid   = this.videoid;
        this.element.dataset.droptask  = "move";
        this.element.classList.add("VideoQueueTile");

        this.artwork                  = new VideoArtwork(MDBVideo, "small");

        this.infobox                  = document.createElement("div");
        this.infobox.classList.add("infobox");

        this.titleelement             = document.createElement("div");
        this.titleelement.textContent = videoname;
        this.titleelement.onclick     = ()=>{this.ShowVideo();};

        this.artistelement            = document.createElement("div");
        this.artistelement.textContent = artistname;
        this.artistelement.classList.add("hlcolor");
        this.artistelement.classList.add("smallfont");
        this.artistelement.onclick    = ()=>{artistsview.ScrollToArtist(artistid);};

        this.infobox.appendChild(this.titleelement);
        if(position > 0)
            this.infobox.appendChild(buttonbox.GetHTMLElement());
        this.infobox.appendChild(this.artistelement);

        this.element.appendChild(this.artwork.GetHTMLElement());
        this.element.appendChild(this.infobox);

        if(position > 0)
            this.BecomeDraggable();
    }



    GetHTMLElement()
    {
        return this.element;
    }



    ShowVideo()
    {
        MusicDB_Request("GetVideo", "ShowVideo", {videoid: this.videoid});
    }
}



class VideoTile
{
    // flagbar is optional
    constructor(MDBVideo, onclick, flagbar)
    {
        let videoid      = MDBVideo.id;
        let videoname    = MDBVideo.name;
        let videorelease = MDBVideo.release;

        this.artwork                  = new VideoArtwork(MDBVideo, "medium");

        this.titleelement             = document.createElement("span");
        this.titleelement.textContent = videoname;
        this.titleelement.classList.add("hlcolor");
        this.titleelement.classList.add("smallfont");

        this.buttonbox                = new ButtonBox_AddVideoToQueue(videoid);

        this.element                  = document.createElement("div");
        this.element.classList.add("VideoTile");
        this.element.appendChild(this.artwork.GetHTMLElement());
        this.element.appendChild(this.buttonbox.GetHTMLElement());
        this.element.appendChild(this.titleelement);
        if(flagbar !== undefined)
            this.element.appendChild(flagbar.GetHTMLElement());
        this.element.onclick = onclick;

        if(MDBVideo.disabled)
            this.SetDisabled();
        else
            this.SetEnabled();
    }


    ReplaceFlagBar(newflagbar)
    {
        let newflagbarelement = newflagbar.GetHTMLElement();
        let oldflagbarelement = this.element.getElementsByClassName("FlagBar")[0];
        this.element.replaceChild(newflagbarelement, oldflagbarelement);
    }

    SetEnabled()
    {
        this.element.dataset.enabled = true;
    }
    SetDisabled()
    {
        this.element.dataset.enabled = false;
    }


    GetHTMLElement()
    {
        return this.element;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

