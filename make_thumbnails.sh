#!/usr/bin/env sh

for collage in `find collages-big -name "*.jpg"`; do
    filename=`basename -- "$collage"`
    convert \
        "$collage" \
        -resize "400^>" \
        -auto-orient \
        "static/collages-small/$filename"
    composite \
        -gravity SouthEast \
        watermark.png \
        "static/collages-small/$filename" \
        "static/collages-small/$filename"
    echo $filename
done
