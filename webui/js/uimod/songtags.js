
"use strict";

/*
 * This function creates and shows a grid of mood tags.
 * 
 * Args:
 *  parentid (str): ID of the HTML element in that the grid shall be placed
 *  controlname (str): Name of the grid to identify if later
 */
function Videotags_ShowMoodControl(parentid, controlname)
{
    // There are no differences between songs and videos at this point
    Songtags_ShowMoodControl(parentid, controlname);
}
function Songtags_ShowMoodControl(parentid, controlname)
{
    if($("#"+parentid).length === 0)
    {
        window.console && console.log("Parent " + parentid + "does not exist!");
        return;
    }

    var moods;
    moods = Tagmanager_GetMoods();

    // Determin grid size
    var columns=0, rows=0;
    for(let mood of moods)
    {
        if(mood.posx == null || mood.posy == null)
            continue;

        if(mood.posx > columns) columns = mood.posx;
        if(mood.posy > rows)    rows    = mood.posy;
    }
    columns += 1; // \_ position starts with 0 - so max posx=3 indicates 4 columns
    rows    += 1; // /

    // Create grid
    var html = "";
    html += CreateGrid(controlname, columns, rows);
    $("#"+parentid).html(html);

    // Create mood buttons
    for(let mood of moods)
    {
        // Get parameters from tag
        let icon, posx, posy, name, btnid;
        icon  = mood.icon;
        posx  = mood.posx;
        posy  = mood.posy;
        name  = mood.name;
        btnid = controlname + "_" + name.replace(/\s+/g, ''); // control name + name of mood

        // Create cell content
        let html = "";
        html += "<div";
        html += " id=\"" + btnid + "\"";
        html += " class=\"moodbutton\"";
        html += " data-button=\"unpressed\"";
        html += " title=\"" + name + "\"";
        html += ">";
        html += icon;
        html += "</div>";

        // Set cell content into cell
        let cellid;
        cellid = GridCellID(controlname, posx, posy);
        $("#"+cellid).html(html);
    }
}


/*
 * This function sets the tags and functionality of a Mood Control for a specific song
 *
 * Args:
 *  controlname (str): To identify the grid
 *  MDBSongTags: The tags of a specific song
 */
function Songtags_UpdateMoodControl(controlname, MDBSongTags)
{
    // Create a list of tags that are set
    var taglist = [];
    for(let tag of MDBSongTags.moods)
        taglist.push(tag.id);

    // Update each mood button
    var moods;
    moods = Tagmanager_GetMoods();

    for(let mood of moods)
    {
        let buttonid;
        buttonid = "#" + controlname + "_" + mood.name.replace(/\s+/g, ''); // control name + name of mood

        let buttonstate;
        if(taglist.indexOf(mood.id) >= 0)
            buttonstate = "pressed";
        else
            buttonstate = "unpressed";

        $(buttonid).attr("data-button", buttonstate);
        $(buttonid).off().on("click",
            function()
            {
                Songtags_onTagButtonClick(buttonid, MDBSongTags.songid, mood.id);
            }
        );
    }

}

function Videotags_UpdateMoodControl(controlname, MDBVideoTags)
{
    // Create a list of tags that are set
    let taglist = [];
    for(let tag of MDBVideoTags.moods)
        taglist.push(tag.id);

    // Update each mood button
    let moods;
    moods = Tagmanager_GetMoods();

    for(let mood of moods)
    {
        let buttonid;
        buttonid = "#" + controlname + "_" + mood.name.replace(/\s+/g, ''); // control name + name of mood

        let buttonstate;
        if(taglist.indexOf(mood.id) >= 0)
            buttonstate = "pressed";
        else
            buttonstate = "unpressed";

        $(buttonid).attr("data-button", buttonstate);
        $(buttonid).off().on("click",
            function()
            {
                Videotags_onTagButtonClick(buttonid, MDBVideoTags.videoid, mood.id);
            }
        );
    }
}


function Songtags_onTagButtonClick(buttonid, songid, tagid)
{
    var buttonstate = $(buttonid).attr("data-button");
    var newstate;

    if(buttonstate == "pressed")
    {
        newstate = "unpressed";
        MusicDB_Request("RemoveSongTag", "UpdateSong", {songid:songid, tagid:tagid});
    }
    else if(buttonstate == "unpressed")
    {
        newstate = "pressed";
        MusicDB_Request("SetSongTag", "UpdateSong", {songid:songid, tagid:tagid});
    }

    $(buttonid).attr("data-button", newstate);
}

function Videotags_onTagButtonClick(buttonid, videoid, tagid)
{
    var buttonstate = $(buttonid).attr("data-button");
    var newstate;

    if(buttonstate == "pressed")
    {
        newstate = "unpressed";
        MusicDB_Request("RemoveVideoTag", "UpdateVideo", {videoid:videoid, tagid:tagid});
    }
    else if(buttonstate == "unpressed")
    {
        newstate = "pressed";
        MusicDB_Request("SetVideoTag", "UpdateVideo", {videoid:videoid, tagid:tagid});
    }

    $(buttonid).attr("data-button", newstate);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

