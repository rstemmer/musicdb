
function HMSToString(h,m,s)
{
    // convert to string
    let ss = ("00"+s).substr(-2);
    let ms = ("00"+m).substr(-2);
    let hs = ("00"+h).substr(-2);

    // create time string hh:mm:ss
    return hs + ":" + ms + ":" + ss;
}

// mm:ss -> sss (Example: "1:23" ->  83)
// mm:   -> sss (Example: "1:"   ->  60)
// m     -> sss (Example: "1"    ->  60)
function TimeStringToSeconds(timestring)
{
    let substr = timestring.split(":");
    let min = "0";
    let sec = "0";

    if(substr.length == 1)
    {
        min = substr[0];
    }
    else
    {
        min = substr[0];
        if(substr[1] != "")
            sec = substr[1];
    }

    let time   = parseInt(min) * 60 + parseInt(sec);
    return time;
}

// sss -> mm:ss (Example: 83 -> "1:23")
function SecondsToTimeString(seconds)
{
    let time;
    if(typeof seconds === "number")
        time = seconds;
    else if(typeof seconds === "string")
        time = parseFloat(seconds);

    if(isNaN(time))
        return null;

    time = Math.round(time);

    let min = Math.floor(time / 60);
    let sec = Math.floor(time % 60);

    // convert to string
    let min_str    = ("  "+min).substr(-2);
    let sec_str    = ("00"+sec).substr(-2);
    let timestring = min_str + ":" + sec_str;
    return timestring;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

