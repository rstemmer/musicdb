
function CreateIntersectionObserver(elementname, callback)
{

    let options = {
            root:       null,
            rootMargin: "10%"
        };

    let trigger  = document.getElementById(elementname);
    let observer = new IntersectionObserver(callback, options);
    observer.observe(trigger);
}


function onDetachableTriggerIntersection(entries, observer)
{
    let element = document.getElementById("detachable_video");

    entries.forEach((entry) => {
            window.console && console.log(entry.intersectionRatio);
            window.console && console.log(entry.isIntersecting);

            if(entry.isIntersecting)
            {
                window.console && console.log("visible");
                element.dataset.detached = "false";
            }
            else
            {
                window.console && console.log("hidden");
                element.dataset.detached = "true";
            }
        });
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

