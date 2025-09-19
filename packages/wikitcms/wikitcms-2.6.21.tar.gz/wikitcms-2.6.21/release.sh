#!/bin/bash

baddeps=""
# check deps
python3 -m build.__init__ || baddeps="python3-build"
if [ -n "${baddeps}" ]; then
    echo "${baddeps} must be installed!"
    exit 1
fi

if [ "$#" != "1" ]; then
    echo "Must pass release version!"
    exit 1
fi

version=$1
name=wikitcms
sed -i -e "s,version=\".*\",version=\"${version}\", g" setup.py || exit 1
sed -i -e "s,__version__ = \".*\",__version__ = \"${version}\", g" src/${name}/__init__.py || exit 1
git add setup.py src/${name}/__init__.py || exit 1
git commit -s -m "Release ${version}" || exit 1
git push || exit 1
git tag -a -m "Release ${version}" ${version} || exit 1
git push origin ${version} || exit 1
python3 -m build . || exit 1
twine upload -r pypi dist/${name}-${version}* || exit 1
