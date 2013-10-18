#! /bin/bash

# http://stackoverflow.com/questions/1955505/parsing-json-with-sed-and-awk
cat twitter.json | grep -Po '"text":.*?[^\\]",' # prints only the text elements (using regex - no nesting, etc.)


