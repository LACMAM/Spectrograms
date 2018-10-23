#! /bin/bash

for f in $( ls daily ); do
  python3 make_image.py daily/$f
done

