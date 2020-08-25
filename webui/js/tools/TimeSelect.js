
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
    constructor(label, videoelement, initialtime, slidericon, reseticon, resetvalue)
    {
        this.elementorientation = "left";
        this.labeltext          = document.createTextNode(label);
        this.initialtime        = initialtime;
        this.resetvalue         = resetvalue;
        this.videoelement       = videoelement;
        this.validationfunction = null;

        this.label              = document.createElement("label");
        this.label.appendChild(this.labeltext);
        this.slider             = new Slider(new SVGIcon(slidericon), (pos)=>{this.onSliderMoved(pos);});
        this.resetbutton        = new SVGIcon(reseticon);
        this.resetbutton.SetTooltip(`Set slider to ${this.resetvalue}`);
        this.inputelement       = document.createElement("input");

        this.element            = document.createElement("div");
        this.element.classList.add("timeselect");
        //let  buttonlabel    = "Current Time";
        //this.gettimeelement = new Button(buttonlabel, ()=>{this.SelectTimeStampFromVideo()});
        //this.parentelement  = null;


        this.inputelement.dataset.valid = "true";
        this.inputelement.type          = "string";
        this.inputelement.value         = initialtime;
        this.inputelement.oninput       = ()=>{this.onInputEvent(event)};

        this._CreateElement();
        return;
    }

    _CreateElement()
    {
        this.element.innerHTML = "";

        if(this.elementorientation == "left")
        {
            //this.element.classList.add("inputbox");
            this.element.appendChild(this.label);
            this.element.appendChild(this.inputelement);
            this.element.appendChild(this.resetbutton.GetHTMLElement());
            this.element.appendChild(this.slider.GetHTMLElement());
            //this.element.appendChild(this.gettimeelement.GetHTMLElement());
        }
        else if(this.elementorientation == "right")
        {
            //this.element.classList.add("inputbox");
            this.element.appendChild(this.slider.GetHTMLElement());
            this.element.appendChild(this.resetbutton.GetHTMLElement());
            this.element.appendChild(this.inputelement);
            this.element.appendChild(this.label);
            //this.element.appendChild(this.gettimeelement.GetHTMLElement());
        }
    }

    SetOrientationLeft()
    {
        this.elementorientation = "left";
        this._CreateElement();
    }

    SetOrientationRight()
    {
        this.elementorientation = "right";
        this._CreateElement();
    }

    onSliderMoved(sliderpos)
    {
        let totaltime = this.videoelement.duration;
        if(isNaN(totaltime))
            return;

        let newposition = Math.round(totaltime * sliderpos);

        this.videoelement.currentTime = newposition;
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
        let time = Math.round(parseFloat(this.inputelement.value));
        if(typeof time !== "number" || isNaN(time))
        {
            return null;
        }
        return time;
    }

    onInputEvent(e)
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


class BeginTimeSelect extends TimeSelect
{
    constructor(label, videoelement, initialtime, resetvalue)
    {
        super(label, videoelement, initialtime, "vBegin", "vMin", resetvalue);
        this.SetOrientationLeft()
    }
}

class EndTimeSelect extends TimeSelect
{
    constructor(label, videoelement, initialtime, resetvalue)
    {
        super(label, videoelement, initialtime, "vEnd", "vMax", resetvalue);
        this.SetOrientationRight()
    }
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

