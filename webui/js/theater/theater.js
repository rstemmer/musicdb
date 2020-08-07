

function onMusicDBConnectionOpen()
{
    window.console && console.log("[MDB] Open");

    MusicDB_Request("GetTags", "UpdateTagsCache");
}
function onMusicDBConnectionError()
{
    window.console && console.log("[MDB] Error");
}
function onMusicDBWatchdogBarks()
{
    window.console && console.log("[MDB] WD Barks");
}
function onMusicDBConnectionClosed()
{
    window.console && console.log("[MDB] Closed");
}

function onMusicDBNotification(fnc, sig, rawdata)
{
}
function onMusicDBMessage(fnc, sig, args, pass)
{
    console.log(">> fnc: "+fnc+"; sig: "+sig);
}


window.onload = function ()
{
    //var cogs;
    //cogs = "<i class=\"fa fa-cog fa-spin fa-fw\"></i>";
    //$("#MainViewContent1").html(cogs);
    //$("#MainViewContent2").html(cogs);
    //$("#MainViewContent3").html(cogs);
    //$("#MainViewContent4").html(cogs);
    //$("#MainViewContent5").html(cogs);
    ConnectToMusicDB();
    CreateIntersectionObserver("detachable_trigger", onDetachableTriggerIntersection);

}





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


function ToggleVideoPanel()
{
    let videopanel = document.getElementById("videopanel");
    if(videopanel.dataset.visible == "true")
        videopanel.dataset.visible = "false";
    else
        videopanel.dataset.visible = "true";

    let panels = document.getElementById("Panels");
    if(panels.dataset.panels == "1")
        panels.dataset.panels = "2";
    else
        panels.dataset.panels = "1";
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

