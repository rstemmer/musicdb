
class VideoTimeFrameSelection
{
    constructor(videoplayer, MDBVideo)
    {
        this.videoplayer        = videoplayer;
        this.videoid            = MDBVideo.id;
        this.vbegin             = MDBVideo.vbegin;
        this.vend               = MDBVideo.vend;
        this.vplaytime          = MDBVideo.playtime;

        this.begintimeselect    = new BeginTimeSelect("Video Begin", this.videoplayer, this.vbegin, 0);
        this.endtimeselect      = new EndTimeSelect(  "Video End",   this.videoplayer, this.vend,   this.vplaytime);

        this.savebutton         = new SVGButton("Save", ()=>{this.onSave();});
        this.savebutton.SetTooltip("Save selected time frame at MusicDB server");
        this.loadbutton         = new SVGButton("Load", ()=>{this.onLoad();});
        this.loadbutton.SetTooltip("Load and reset selected time frame from MusicDB server");

        this.element            = document.createElement("div");
        this.element.classList.add("videotimeframeselection");
        this.element.classList.add("flex-column");
        this.element.classList.add("frame");

        this.controlboxrow      = document.createElement("div");
        this.controlboxrow.classList.add("flex-row");
        this.controlboxrow.classList.add("vtfs_controlbox");
        this.controltitle       = document.createElement("span");
        this.controltitle.innerText = "Select time frame that will be played";
        this.controlboxrow.appendChild(this.controltitle);
        this.controlboxrow.appendChild(this.loadbutton.GetHTMLElement());
        this.controlboxrow.appendChild(this.savebutton.GetHTMLElement());

        this.timeselectrow      = document.createElement("div");
        this.timeselectrow.classList.add("flex-row");
        this.timeselectrow.classList.add("vtfs_timeselection");
        this.timeselectrow.appendChild(this.begintimeselect.GetHTMLElement());
        this.timeselectrow.appendChild(this.endtimeselect.GetHTMLElement());

        this.messageboxrow      = document.createElement("div");
        this.messageboxrow.classList.add("flex-row");
        this.messageboxrow.classList.add("vtfs_messagebox");

        this.errormessage_begin = document.createElement("div");
        this.errormessage_end   = document.createElement("div");
        this.errormessage_begin.classList.add("vtfs_errormessage");
        this.errormessage_end.classList.add("vtfs_errormessage");
        this.ClearErrorMessage("begin");
        this.ClearErrorMessage("end");
        this.messageboxrow.appendChild(this.errormessage_begin);
        this.messageboxrow.appendChild(this.errormessage_end);


        this.element.appendChild(this.controlboxrow);
        this.element.appendChild(this.timeselectrow);
        this.element.appendChild(this.messageboxrow);

        this.begintimeselect.SetValidationFunction((time) => 
            {
                let endtime = this.endtimeselect.GetSelectedTime();
                if(endtime == null)
                    return true;

                this.ClearErrorMessage("begin");

                if(time < 0)
                {
                    this.ShowErrorMessage("begin", "Negative time is not allowed");
                    return false;
                }

                if(time < endtime)
                    return true;

                let beginstr = SecondsToTimeString(time);
                let endstr   = SecondsToTimeString(endtime);
                this.ShowErrorMessage("begin", `Invalid time: Begin (${beginstr}) >= End (${endstr}) not allowed`);
                return false;
            }
        );

        this.endtimeselect.SetValidationFunction((time) =>
            {
                let begintime = this.begintimeselect.GetSelectedTime();
                if(begintime == null)
                    return true;

                this.ClearErrorMessage("end");

                if(time < 0)
                {
                    this.ShowErrorMessage("end", "Negative time is not allowed");
                    return false;
                }

                if(time > this.vplaytime)
                {
                    let timestr = SecondsToTimeString(time);
                    let playstr = SecondsToTimeString(this.vplaytime);
                    this.ShowErrorMessage("end", `Invalid time: End (${timestr}) greater than maximum play time (${playstr}) not allowed`);
                    return false;
                }

                if(time > begintime)
                    return true;

                let beginstr = SecondsToTimeString(begintime);
                let endstr   = SecondsToTimeString(time);
                this.ShowErrorMessage("end", `Invalid time: End (${endstr}) <= Begin (${beginstr}) not allowed`);
                return false;
            }
        );
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // Call this after the element is append to the DOM
    Initialize()
    {
        this.begintimeselect.Reset();
        this.endtimeselect.Reset();
    }



    ShowErrorMessage(side, message)
    {
        let msgbox;
        if(side == "begin")
            msgbox = this.errormessage_begin
        else if(side == "end")
            msgbox = this.errormessage_end
        else
            return;

        window.console && console.log(message);
        msgbox.innerText       = message;
        msgbox.dataset.visible = true;
        return;
    }
    ClearErrorMessage(side)
    {
        let msgbox;
        if(side == "begin")
            msgbox = this.errormessage_begin
        else if(side == "end")
            msgbox = this.errormessage_end
        else
            return;

        msgbox.innerText       = "";
        msgbox.dataset.visible = false;
        return;
    }



    onSave()
    {
        window.console && console.log("SetVideoTimeFrame disabled for debugging reasons");
        window.console && console.log("begin = " + this.begintimeselect.GetSelectedTime());
        window.console && console.log("end   = " + this.endtimeselect.GetSelectedTime());
        //MusicDB_Call("SetVideoTimeFrame", 
        //    {
        //        videoid: this.videoid,
        //        begin:   this.begintimeselect.GetSelectedTime(),
        //        end:     this.endtimeselect.GetSelectedTime()
        //    });
    }

    onLoad()
    {
        this.Initialize();
    }
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

