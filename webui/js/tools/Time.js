
function HMSToString(h,m,s)
{
    // convert to string
    let ss = ("00"+s).substr(-2);
    let ms = ("00"+m).substr(-2);
    let hs = ("00"+h).substr(-2);

    // create time string hh:mm:ss
    return hs + ":" + ms + ":" + ss;
}

function SecondsToTimeString(seconds)
{
    let time;
    window.console && console.log(seconds);
    window.console && console.log(typeof seconds);
    if(typeof seconds === "number")
        time = seconds;
    else if(typeof seconds === "string")
        time = parseFloat(seconds);

    window.console && console.log(time);
    if(isNaN(time))
        return null;

    let min = time / 60;
    let sec = Math.floor(time % 60);

    // convert to string
    let min_str = ("00"+min).substr(-2);
    let sec_str = ("00"+sec).substr(-2);

    return min_str + ":" + sec_str;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

