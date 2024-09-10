#! /bin/bash

zip $( dirname -- $( dirname -- ${BASH_SOURCE[0]} ) )/releases/render_preset * -x resources/ *.zip
