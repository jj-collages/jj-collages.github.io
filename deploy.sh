#!/usr/bin/env sh
# fail if any command fails
set -e
set -o xtrace
# make sure we're on the develop branch
git checkout develop
# build the website there (outputed in the unversioned _build directory)
make
# copy _build to /tmp
if [ -d /tmp/_build ]; then
    rm -rf /tmp/_build
fi
cp -r _build /tmp/_build
# checkout main branch, containing the static website
git checkout main
# copy build content here
cp -r /tmp/_build/* .
# push that to the repo
git add .
DATE=`date`
git commit -m "deploy: ${DATE}"
git push --force origin main
