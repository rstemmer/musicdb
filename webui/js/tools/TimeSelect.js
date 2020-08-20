
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
    constructor(label, videoelementid, initialtime)
    {
        this.element        = document.createElement("div");
        this.videoelementid = videoelementid;
        let  buttonlabel    = "Current Time";
        this.gettimeelement = new Button(buttonlabel, ()=>{this.SelectTimeStampFromVideo()});
        this.inputelement   = document.createElement("input");
        this.labelelement   = document.createElement("label");
        this.labeltext      = document.createTextNode(label);
        this.validationfunction = null;
        this.parentelement  = null;

        this.labelelement.appendChild(this.labeltext);

        this.inputelement.type = "number";
        this.inputelement.value= initialtime;
        this.inputelement.min  = 0.0;
        this.inputelement.step = 0.1;

        this.element.classList.add("inputbox");
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

        window.console && console.log(time);

        this.inputelement.value = time;
        return;
    }

    GetHTMLElement()
    {
        return this.element;
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

