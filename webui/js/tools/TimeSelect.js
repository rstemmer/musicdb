
class Button
{
    constructor(label, onclick)
    {
        this.element      = document.createElement("button");
        let  labelelement = document.createTextNode(label);
        this.element.appendChild(labelelement);
        this.element.onclick = onclick;
        return;
    }

    BecomeChildOf(parentelement)
    {
        parentelement.appendChild(this.element);
        return;
    }
}

class TimeSelect
{
    constructor(label, videoelementid)
    {
        this.videoelementid = videoelementid;
        this.gettimeelement = new Button("Current Time", ()=>{this.SelectTimeStampFromVideo()});
        this.inputelement   = document.createElement("input");
        this.labelelement   = document.createTextNode(label);
        this.validationfunction = null;
        this.parentelement  = null;
        return;
    }

    SetValidationFunction(fnc)
    {
        this.validationfunction = fnc;
        return;
    }

    GetSelectedTime()
    {
        let time = parseFloat(this.inputelement.value);
        if(typeof time !== "number" || isNaN(time))
        {
            return null;
        }
        return time;
    }

    ShowErrorMessage(message)
    {
        window.console && console.log(message);
        let errormessage = document.createTextNode(message);
        let errorelement = document.createElement("span");
        errorelement.appendChild(errormessage);

        if(this.parentelement)
            this.parentelement.appendChild(errorelement);
        return;
    }

    SelectTimeStampFromVideo()
    {
        let video = document.getElementById(this.videoelementid);
        let time  = video.currentTime;

        if(this.validationfunction)
        {
            let retval = this.validationfunction(time);
            if(typeof retval === "string")
                this.ShowErrorMessage(retval);

            if(retval !== true)
                return;
        }

        this.inputelement.value = time;
        return;
    }

    BecomeChildOf(parentelement)
    {
        this.parentelement = parentelement;
        this.parentelement.appendChild(this.labelelement);
        this.parentelement.appendChild(this.inputelement);
        this.gettimeelement.BecomeChildOf(this.parentelement);
        return;
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

