
"use strict";

/*
 *
 * Requirements:
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 *
 */

var Tagmanager_TagCache = null;

/**
 * This Method updates the tags-cache that hold all available tags.
 *
 * This method should be called whenever the MusicDB server responses with the *fnc* name set to "GetTags".
 *
 * The genres get sorted by its posx attribute
 *
 * @param {MDBTags} MDBTags - A Dictionary with lists of tags for each class
 *
 * @returns *nothing*
 */
function Tagmanager_onGetTags(MDBTags)
{
    Tagmanager_TagCache = MDBTags;

    // Sort genre by x-position (list-position)
    Tagmanager_TagCache.genres.sort(
        function (a, b)
        {
            if (a.posx > b.posx)
                    return 1;
            if (a.posx < b.posx)
                      return -1;
            return 0;
        }
        );
}


/**
 * @returns {MDBTag-list} This method returns *all tags* that are available in the music database separated by tagclass
 */
function Tagmanager_GetTags()
{
    return Tagmanager_TagCache;
}

/**
 * @returns {MDBTag-list} This method returns the list of *genres* that are available in the music database
 */
function Tagmanager_GetGenres()
{
    return Tagmanager_TagCache.genres;
}

/**
 * @returns {MDBTag-list} This method returns the list of *subgenres* that are available in the music database
 */
function Tagmanager_GetSubgenres()
{
    return Tagmanager_TagCache.subgenres;
}

/**
 * @returns {MDBTag-list} This method returns the list of *moods* that are available in the music database
 */
function Tagmanager_GetMoods()
{
    return Tagmanager_TagCache.moods;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

