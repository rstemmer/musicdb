
"use strict";

/*
 * These functions handle the connection to the server.
 * Call  ConnectToMusicDB  to connect.
 * Be sure the following functions are available in the main js file of the module:
 *  - onMusicDBConnectionOpen();
 *  - onMusicDBConnectionError();
 *  - onMusicDBConnectionClosed();
 *  - onMusicDBMessage(fnc, sig, args, pass);
 * Optional:
 *  - onMusicDBNotification(fnc, sig, rawdata);
 *  - onMusicDBWatchdogBarks();
 *
 * Furthermore the following functions can be used to send data:
 *  - MusicDB_Call(fncname, arguments)
 *  - MusicDB_Request(fncname, fncsig, arguments, pass)
 *
 * All functions starting with MDB_ are private and should never be called from other code
 * Same with all globale variables
 */

var socket              = null;
var WATCHDOG_RUN        = true;
var WATCHDOG_INTERVAL   = 5000; //[ms] (here, 5 times longer than a heartbeat)
var WEBSOCKET_URL       = "wss://" + location.hostname + ":9000";


///////////////////////////////////////////////////////////////////////////////
// Connect to the MDB Websochet server ////////////////////////////////////////

/**
 * This function established a connection to the server.
 * If there is already a connection, it will be closed first.
 *
 * This function also implements the following methods of the WebSocket class as also shown in the picture above:
 *  
 *  * onopen
 *  * onclose
 *  * onerror
 *  * onmessage
 *
 * @returns *nothing*
 */
function ConnectToMusicDB()
{
    // ! socket is global !
    // if there is an open connecten, close it first
    if(socket !== null)
        socket.close();

    // Create websocket interface
    socket = new WebSocket(WEBSOCKET_URL);
    socket.onopen = function()
    {
        if(typeof onMusicDBConnectionOpen === "function")
            onMusicDBConnectionOpen();
    };
    socket.onclose = function(e)
    {
        MDB_StopWebsocketWatchdog();
        if(this.readyState != this.CLOSING && this.readyState != this.CLOSED)
        {
            // some shit happend… Lets clean it up 
            // ( http://www.w3.org/TR/2011/WD-websockets-20110419/ )
            this.readyState = this.CLOSING;
            if(typeof onMusicDBConnectionError === "function")
                onMusicDBConnectionError();
        }
        else
        {
            if(typeof onMusicDBConnectionClosed === "function")
                onMusicDBConnectionClosed();
        }
    };
    socket.onerror = function(e)
    {
        MDB_StopWebsocketWatchdog();
        if(typeof onMusicDBConnectionError === "function")
            onMusicDBConnectionError();
    };
    socket.onmessage = function(e)
    {
        // reset WD every time a packet comes
        MDB_ResetWebsocketWatchdog();

        var packet = JSON.parse(e.data);

        var fnc  = packet.fncname;
        var sig  = packet.fncsig;
        var args = packet.arguments;
        var pass = packet.pass;

        if(packet.method === "notification")
        {
            if(typeof onMusicDBNotification === "function")
                onMusicDBNotification(fnc, sig, args);
        }
        else
        {
            onMusicDBMessage(fnc, sig, args, pass);
        }
    };
}


///////////////////////////////////////////////////////////////////////////////
// Websocket Watchdog /////////////////////////////////////////////////////////

let timeouthandler = null;
let disablewd      = false; // To temporary disable the watchdog (for example when MPD is not running)

/**
 * This function can be used to temporary disable the watchdog.
 * For example when MPD is disconnected and cannot provide the clients with the current state every second.
 */
function MDB_DisableWatchdog()
{
    disablewd = true;
    MDB_ResetWebsocketWatchdog();
}


/**
 * This function can be used to enable the watchdog after it was disabled.
 */
function MDB_EnableWatchdog()
{
    disablewd = true;
    MDB_StopWebsocketWatchdog();
}

/**
 * This is the callback funtion of the timer.
 * On timeout, this function gets called.
 * It first calles the ``onMusicDBWatchdogBarks`` function that must be implemented by the user.
 * Next a reconnection gets triggerd calling :js:func:`ConnectToMusicDB`.
 *
 * @returns *nothing*
 */
function MDB_WebsocketWatchdog()
{
    // call an optional callback
    if(typeof onMusicDBWatchdogBarks === "function")
        onMusicDBWatchdogBarks();

    // reconnect
    ConnectToMusicDB();

    // no restart of the timer necessary 
    // it will be done by the server with each event including a heatbeat
}

/**
 * This method stops the watchdog timer.
 *
 * @returns *nothing*
 */
function MDB_StopWebsocketWatchdog()
{
    if(timeouthandler !== null)
        clearTimeout(timeouthandler);
}

/**
 * This method starts and resets the watchdog timer if ``WATCHDOG_RUN`` is ``true``.
 * The interval is determined by ``WATCHDOG_INTERVAL``.
 * When the timer gets not reset until the interval is over, the :js:func:`MDB_WebsocketWatchdog` function gets called.
 *
 * @returns *nothing*
 */
function MDB_ResetWebsocketWatchdog()
{
    if(WATCHDOG_RUN === true && disablewd === false)
    {
        MDB_StopWebsocketWatchdog();
        timeouthandler = setTimeout("MDB_WebsocketWatchdog()", WATCHDOG_INTERVAL);
    }
}

///////////////////////////////////////////////////////////////////////////////
// Protocol ///////////////////////////////////////////////////////////////////

/**
 * This function calls a function on the MusicDB server using the MusicDB WebSocket API.
 * It uses the method *call*, so *fncsig* and *pass* are ``null`` by default.
 *
 * @param {string} fncname - Name of the function that shall be called
 * @param {object} args - optional object with all argumens for the called function
 * @returns *nothing*
 */
function MusicDB_Call(fncname, args)
{
    args = args || null;
    var packet = {
        method:     "call",
        fncname:    fncname,
        fncsig:     null,
        arguments:  args,
        pass:       null
    }
    MDB_SendPacket(packet);
}

/**
 * This function calls a function on the MusicDB server using the MusicDB WebSocket API.
 * It uses the *request* method so that the server responses to this call.
 *
 * The *fncsig* helps to associate the response with the call.
 * It furthermore can be used to define how the response shall be processed.
 *
 * The *pass* argument can be used to pass data through the server back to the response handler.
 * For example an element ID of the DOM, in that a result shall be printed.
 *
 * If *fncsig* or *pass* are not set (undefined) they will be set to the valid value ``null``.
 *
 * @param {string} fncname - Name of the function that shall be called
 * @param {string} fncsig - signature string of the function that made the request
 * @param {object} args - optional object with all argumens for the called function
 * @param {object} pass - optional object with data hat will be passed throug the server and will be part of the response.
 * @returns *nothing*
 */
function MusicDB_Request(fncname, fncsig, args, pass)
{
    pass = pass || null;
    args = args || null;
    var packet = {
        method:     "request",
        fncname:    fncname,
        fncsig:     fncsig,
        arguments:  args,
        pass:       pass
    }
    MDB_SendPacket(packet);
}

/**
 * Similar to :js:func:`MusicDB_Request`.
 * The response will be send to all connected clients, not just to the caller.
 */
function MusicDB_Broadcast(fncname, fncsig, args, pass)
{
    pass = pass || null;
    args = args || null;
    var packet = {
        method:     "broadcast",
        fncname:    fncname,
        fncsig:     fncsig,
        arguments:  args,
        pass:       pass
    }
    MDB_SendPacket(packet);
}

///////////////////////////////////////////////////////////////////////////////
// Send Packets via Websockets ////////////////////////////////////////////////

/**
 * This is an internal function used by :js:func:`MusicDB_Call`, :js:func:`MusicDB_Request` and :js:func:`MusicDB_Broadcast`.
 * It implements the low level send function that creates a JSON string which will be send to the MusicDB server using WebSockets.
 *
 * @returns {boolean} ``true`` on success, otherwise ``false``
 */
function MDB_SendPacket(packet)
{
    var buffer;
    buffer = JSON.stringify(packet);
    try
    {
        socket.send(buffer);
    }
    catch(error)
    {
        return false;
    }
    return true;
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

