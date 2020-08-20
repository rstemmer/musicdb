
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

    GetHTMLElement(parentelement)
    {
        return this.element;
    }
}

class TimeSelect
{
    constructor(label, videoelementid)
    {
        this.element        = document.createElement("div");
        this.videoelementid = videoelementid;
        this.gettimeelement = new Button("Current Time", ()=>{this.SelectTimeStampFromVideo()});
        this.inputelement   = document.createElement("input");
        this.labelelement   = document.createTextNode(label);
        this.validationfunction = null;
        this.parentelement  = null;

        this.element.appendChild(this.labelelement);
        this.element.appendChild(this.inputelement);
        this.element.appendChild(this.gettimeelement.GetHTMLElement());
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
        let errormessage = document.createTextNode(message);
        let errorelement = document.createElement("span");
        errorelement.appendChild(errormessage);

        this.element.appendChild(errorelement);
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

    GetHTMLElement()
    {
        return this.element;
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

