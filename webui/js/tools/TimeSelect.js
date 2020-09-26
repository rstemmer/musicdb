
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
    // reseticonname and resetvalue are optional.
    // If reseticonname is undefined, there will be no reset functionality
    // The slider covers the range from 0 to maxtime
    constructor(label, videoelement, initialtime, maxtime, slidericon, reseticonname, resetvalue)
    {
        this.elementorientation = "left";
        this.labeltext          = document.createTextNode(label);
        this.initialtime        = initialtime;
        this.maxtime            = maxtime;
        this.resetvalue         = resetvalue;
        this.videoelement       = videoelement;
        this.validationfunction = null;

        this.label              = document.createElement("label");
        this.label.appendChild(this.labeltext);
        this.slider             = new Slider(new SVGIcon(slidericon), (pos)=>{this.onSliderMoved(pos);});
        this.slider.AddMouseWheelEvent((event)=>{this.onMouseWheel(event)});
        
        if(reseticonname !== undefined)
        {
            this.resetbutton        = new SVGButton(reseticonname, ()=>{this.SetNewTime(this.resetvalue);});
            this.resetbutton.SetTooltip(`Set slider to ${SecondsToTimeString(this.resetvalue)}`);
        }

        this.thistimebutton     = new SVGButton("vThis", ()=>{this.SelectTimeFromVideo();});
        this.thistimebutton.SetTooltip(`Select current time from video`);
        
        this.inputelement       = document.createElement("input");

        this.element            = document.createElement("div");
        this.element.classList.add("timeselect");


        this.inputelement.dataset.valid = "true";
        this.inputelement.type          = "string";
        this.inputelement.oninput       = (event)=>{this.onTextInput(event)};
        this.inputelement.onwheel       = (event)=>{this.onMouseWheel(event)};


        this._CreateElement();
        this.Reset();
        // The sliders dimensions are not yet known because it is not placed in the DOM
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
            if(this.resetbutton !== undefined)
                this.element.appendChild(this.resetbutton.GetHTMLElement());
            this.element.appendChild(this.slider.GetHTMLElement());
        }
        else if(this.elementorientation == "right")
        {
            this.element.appendChild(this.slider.GetHTMLElement());
            if(this.resetbutton !== undefined)
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
        let totaltime = this.maxtime;
        let newtime   = Math.round(totaltime * sliderpos);

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

    onMouseWheel(event)
    {
        // When using the mouse wheel on an input element, do not scroll the page
        event.preventDefault();

        let newtime = this.GetSelectedTime();

        // Increment/Decrement 1s per mouse wheel step
        if(event.deltaY < 0)
            newtime += 1;
        else if(event.deltaY > 0 && newtime > 0)
            newtime -= 1;
        else
            return;

        // Validate new time
        if(! this.ValidateNewTime(newtime))
            return;

        // Update other controls
        this.SetNewTime(newtime);
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



    // Expects a valid time as number in seconds
    SetNewTime(newtime)
    {
        this.videoelement.currentTime = newtime;
        this.inputelement.value       = SecondsToTimeString(newtime);
        this.slider.SetPosition(newtime / this.maxtime);
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
        this.slider.SetPosition(this.initialtime / this.maxtime);
        return;
    }



}


class BeginTimeSelect extends TimeSelect
{
    constructor(label, videoelement, initialtime, maxtime, resetvalue)
    {
        super(label, videoelement, initialtime, maxtime, "vBegin", "vMin", resetvalue);
        this.SetOrientationLeft()
    }
}

class EndTimeSelect extends TimeSelect
{
    constructor(label, videoelement, initialtime, maxtime, resetvalue)
    {
        super(label, videoelement, initialtime, maxtime, "vEnd", "vMax", resetvalue);
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

