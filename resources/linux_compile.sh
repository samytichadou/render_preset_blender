#! /bin/bash

# TODO Make it executable from elsewhere (zip command with wildcard problem)


### GET VERSION

cat $( dirname -- $( dirname -- ${BASH_SOURCE[0]} ) )"/blender_manifest.toml" | { while read line
do
    if  [[ $line == "version = "* ]] ;
    then
        VERSION=`echo $line | cut -d '"' -f 2`
        VERSION=${VERSION//./_}
        echo version : $VERSION
    fi
done


### CREATE RELEASE

OUTPUTPATH="$( dirname -- $( dirname -- ${BASH_SOURCE[0]} ) )$OUTPUTPATH/releases/render_preset_$VERSION"

# Removing if existing file
echo Trying to remove : $OUTPUTPATH.zip
rm -f -- $OUTPUTPATH.zip

# Creating archive
echo Creating : $OUTPUTPATH
# # zip $( dirname -- $( dirname -- ${BASH_SOURCE[0]} ) )$OUTPUTPATH * -x resources/ *.zip
zip $OUTPUTPATH * -x __pycache__/ releases/ resources/ *.zip

###

}
