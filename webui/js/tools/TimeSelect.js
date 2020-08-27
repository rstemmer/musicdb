
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
    constructor(label, videoelement, initialtime, slidericon, reseticonname, resetvalue)
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
        
        this.resetbutton        = new SVGButton(reseticonname, ()=>{this.SetNewTime(this.resetvalue);});
        this.resetbutton.SetTooltip(`Set slider to ${this.resetvalue}`);

        this.thistimebutton     = new SVGButton("vThis", ()=>{this.SelectTimeFromVideo();});
        this.thistimebutton.SetTooltip(`Select current time from video`);
        
        this.inputelement       = document.createElement("input");

        this.element            = document.createElement("div");
        this.element.classList.add("timeselect");


        this.inputelement.dataset.valid = "true";
        this.inputelement.type          = "string";
        this.inputelement.oninput       = ()=>{this.onTextInput(event)};

        this._CreateElement();
        this.Reset();
        // SetNewTime positions the slider depending on the video-element duration attribute.
        // This attribute is usually not set when this constructor is called because it is loaded
        // from the video meta data that is still on its way.
        // Furthermore the sliders dimensions are not yet known because it is not placed in the DOM
        return;
    }

    _CreateElement()
    {
        this.element.innerHTML = "";

        if(this.elementorientation == "left")
        {
            this.element.appendChild(this.label);
            this.element.appendChild(this.inputelement);
            this.element.appendChild(this.thistimebutton.GetHTMLElement());
            this.element.appendChild(this.resetbutton.GetHTMLElement());
            this.element.appendChild(this.slider.GetHTMLElement());
        }
        else if(this.elementorientation == "right")
        {
            this.element.appendChild(this.slider.GetHTMLElement());
            this.element.appendChild(this.resetbutton.GetHTMLElement());
            this.element.appendChild(this.thistimebutton.GetHTMLElement());
            this.element.appendChild(this.inputelement);
            this.element.appendChild(this.label);
        }
        return;
    }

    GetHTMLElement()
    {
        return this.element;
    }



    SetOrientationLeft()
    {
        this.elementorientation = "left";
        this._CreateElement();
        return;
    }

    SetOrientationRight()
    {
        this.elementorientation = "right";
        this._CreateElement();
        return;
    }

    SetValidationFunction(fnc)
    {
        this.validationfunction = fnc;
        return;
    }



    onSliderMoved(sliderpos)
    {
        let totaltime = this.videoelement.duration;
        if(isNaN(totaltime))
            return;

        let newtime = Math.round(totaltime * sliderpos);

        // Validate new position
        if(! this.ValidateNewTime(newtime))
            return;

        // Update other controls
        this.SetNewTime(newtime)
        return;
    }

    onTextInput(e)
    {
        let newtime = this.GetSelectedTime();

        // Validate new time
        if(! this.ValidateNewTime(newtime))
            return;

        // Update other controls
        this.SetNewTime(newtime);
        return;
    }



    SelectTimeFromVideo()
    {
        let newtime = this.videoelement.currentTime;

        // Validate new time
        if(! this.ValidateNewTime(newtime))
            return;

        // Update other controls
        this.SetNewTime(newtime);
        return;
    }



    // Expects a valid time as number
    SetNewTime(newtime)
    {
        this.videoelement.currentTime = newtime;
        this.inputelement.value       = SecondsToTimeString(newtime);
        this.slider.SetPosition(newtime / this.videoelement.duration);
        return;
    }



    GetSelectedTime()
    {
        let timestring = this.inputelement.value;
        let time       = TimeStringToSeconds(timestring);

        if(typeof time !== "number" || isNaN(time))
            return null;

        return time;
    }



    ValidateNewTime(time)
    {
        if(this.validationfunction)
        {
            let retval = this.validationfunction(time);
            if(typeof retval === "string")
            {
                this.ShowErrorMessage(retval);
                retval = false;
            }

            if(retval === true)
            {
                this.inputelement.dataset.valid="true";
                return true;
            }
            else
            {
                this.inputelement.dataset.valid="false";
                return false;
            }
        }
        else
        {
            this.inputelement.dataset.valid="true";
            return true;    // Always true when no validation function is defined
        }
    }



    Reset()
    {
        this.inputelement.value = SecondsToTimeString(this.initialtime);
        this.slider.SetPosition(this.initialtime / this.videoelement.duration);
        return;
    }



    ShowErrorMessage(message)
    {
        window.console && console.log(message);
        return;
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
    
    Reset()
    {
        super.Reset();
        if(this.resetvalue > 0)
            this.slider.SetPosition(this.initialtime / this.resetvalue);
    }
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

