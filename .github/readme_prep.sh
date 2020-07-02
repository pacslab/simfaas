#! /bin/bash

convert_readme()
{
    PANDOC_DOCKER="nimamahmoudi/pandoc"
    REPO_ROOT=$(pwd)
    FOLDER=$1
    FILE="README.md"
    docker run -t --rm --mount src=$REPO_ROOT/,target=/repo,type=bind $PANDOC_DOCKER /bin/bash -c \
        "cd /repo/$FOLDER && pandoc $FILE -t rst -o README.rst"
}


echo "Converting README.md..."
convert_readme .
echo "Done!"