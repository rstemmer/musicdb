
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
        this.initialtime    = initialtime;
        let  buttonlabel    = "Current Time";
        this.gettimeelement = new Button(buttonlabel, ()=>{this.SelectTimeStampFromVideo()});
        this.inputelement   = document.createElement("input");
        this.labelelement   = document.createElement("label");
        this.labeltext      = document.createTextNode(label);
        this.validationfunction = null;
        this.parentelement  = null;

        this.labelelement.appendChild(this.labeltext);

        this.inputelement.dataset.valid="true";
        this.inputelement.type = "number";
        this.inputelement.value= initialtime;
        this.inputelement.min  = 0.0;
        this.inputelement.step = 0.1;
        this.inputelement.oninput = ()=>{this.InputEvent()};

        this.element.classList.add("inputbox");
        this.element.appendChild(this.labelelement);
        this.element.appendChild(this.inputelement);
        this.element.appendChild(this.gettimeelement.GetHTMLElement());
        return;
    }

    Reset()
    {
        this.inputelement.value = this.initialtime;
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

    InputEvent()
    {
        let time = this.inputelement.value;

        if(this.validationfunction)
        {
            let retval = this.validationfunction(time);
            if(typeof retval === "string")
                this.ShowErrorMessage(retval);

            if(retval !== true)
            {
                this.inputelement.dataset.valid="false";
                return;
            }
            else
            {
                this.inputelement.dataset.valid="true";
            }
        }
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
            {
                this.inputelement.dataset.valid="false";
                return;
            }
        }

        this.inputelement.value = time;
        this.inputelement.dataset.valid="true";
        return;
    }

    GetHTMLElement()
    {
        return this.element;
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

