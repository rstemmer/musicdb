
function CreateIntersectionObserver(elementname, callback)
{

    let options = {
            root:       null,
            rootMargin: "10%"
        };

    let trigger  = document.getElementById(elementname);
    // This feature was annoying because the detached video covered parts of the queue and controls.
    //let observer = new IntersectionObserver(callback, options);
    //observer.observe(trigger);
}


function onDetachableTriggerIntersection(entries, observer)
{
    let element = document.getElementById("detachable_video");
    let video   = document.getElementById("VideoStreamPlayer");

    entries.forEach((entry) => {
            window.console && console.log(entry.intersectionRatio);
            window.console && console.log(entry.isIntersecting);

            if(entry.isIntersecting)
            {
                element.dataset.detached = "false";
                video.dataset.detached   = "false";
            }
            else
            {
                element.dataset.detached = "true";
                video.dataset.detached   = "true";
            }
        });
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

