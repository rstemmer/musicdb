#!/usr/bin/env bash

SessionName="MusicDB"
ScriptDirectory="$(dirname "$(readlink -f $0)")"
StartDirectory="$(dirname "$ScriptDirectory")"

RootWindowName="Project"
SourceWindowName="Source"
TestWindowName="Testing"

tmux has-session -t "$SessionName" 2>/dev/null

# If session does not exists, create it
if [[ $? != 0 ]] ; then
    # This also creates the first window
    tmux new-session -d -s "$SessionName" -c "$StartDirectory/." -n "$RootWindowName"

    # Setup Source Window
    tmux new-window   -t "$SessionName:1" -c "$StartDirectory/musicdb" -n "$SourceWindowName"

    # Setup Testing Window
    tmux new-window   -t "$SessionName:2" -c "/var/log/musicdb" -n "$TestWindowName"
    tmux split-window -t "$SessionName:2" -c "$StartDirectory/scripts" -h -l '50%'
    tmux split-window -t "$SessionName:2" -c "$StartDirectory/scripts" -v
fi

# Enter Session
tmux attach-session -t "$SessionName"

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
