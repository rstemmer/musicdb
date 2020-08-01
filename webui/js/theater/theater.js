

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

}



const numSteps = 20.0;

let boxElement;

window.addEventListener("load", (event) => {
      boxElement = document.getElementById("popable_trigger");

      createObserver();
    }, false);


function createObserver()
{
    let observer;
    let thresholds = [];
    thresholds.push(0.0);
    thresholds.push(0.25);
    thresholds.push(0.5);
    thresholds.push(0.75);
    thresholds.push(1.0);

    let options = {
            root:       null,
            rootMargin: "10%"/*,
            thresholds: thresholds*/
        };

    observer = new IntersectionObserver(handleIntersect, options);
    observer.observe(boxElement);
}


function handleIntersect(entries, observer)
{
    let element = document.getElementById("popable_video");

    entries.forEach((entry) => {
            window.console && console.log(entry.intersectionRatio);
            window.console && console.log(entry.isIntersecting);

            if(entry.isIntersecting)
            {
                window.console && console.log("visible");
                element.classList.remove("popable_out");
                element.classList.add("popable_in");
            }
            else
            {
                window.console && console.log("hidden");
                element.classList.remove("popable_in");
                element.classList.add("popable_out");
            }
        });
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

