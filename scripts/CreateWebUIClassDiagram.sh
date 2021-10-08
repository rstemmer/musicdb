#!/usr/bin/env zsh

{ echo "digraph webui {\nnode[shape=record]\nedge[arrowhead=empty]" ; find "../webui/" -iname "*.js" -exec grep extends {} \; | sed 's/extends/->/g' | cut -d ' ' -f 2,3,4 ; echo "}" } | dot -T png -o WebUI\ UML\ Class\ Diagram.png

