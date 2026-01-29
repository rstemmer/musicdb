#!/usr/bin/env zsh

{ echo "digraph webui {\nnode[shape=record]\nedge[arrowhead=empty]" ; find "../webui/" -iname "*.js" ! -name WebUI.js -exec grep extends {} \; | sed 's/extends/->/g' | cut -d ' ' -f 2,3,4 ; echo "}" } | dot -Grankdir=RL -T png -o WebUI\ UML\ Class\ Diagram.png

