#!/bin/bash
# to install: $ ln -s ../../pre-commit-check.sh .git/hooks/pre-commit

function handle_exit {
    if [ $? -ne 0 ]; then
        EXITCODE=1
    fi
}

EXITCODE=0

echo 'Running tests'
bin/test; handle_exit

echo '====== Running ZPTLint ======'
for pt in `find src/slc/cart/ -name "*.pt"` ; do bin/zptlint $pt; done
for xml in `find src/slc/cart/ -name "*.xml"` ; do bin/zptlint $xml; done
for zcml in `find src/slc/cart/ -name "*.zcml"` ; do bin/zptlint $zcml; done

echo '====== Running PyFlakes ======'
bin/zopepy setup.py flakes; handle_exit

echo '====== Running pep8 =========='
bin/pep8 --ignore=E501 --count src/slc/cart; handle_exit
bin/pep8 --ignore=E501 --count setup.py; handle_exit

if [ $EXITCODE -ne 0 ]; then
    exit 1
fi
