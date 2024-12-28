#!/bin/bash

# imagemagick required for testing

# error flag
err=0

# default call, but written to null
./labyrinth.py -o stdout > /dev/null

# check valid parameters
echo "parameter test"
./labyrinth.py -s 53 -o stdout > /dev/null
./labyrinth.py -l 0.5 -o stdout > /dev/null
./labyrinth.py -r 1.9 -o stdout > /dev/null
./labyrinth.py -b 0.4 -o stdout > /dev/null
./labyrinth.py -c Greys -o stdout > /dev/null

# check valid sizes 
echo "size test"
./labyrinth.py -s 1 -o stdout &> /dev/null
./labyrinth.py -s 3 -o stdout &> /dev/null
./labyrinth.py -s 5 -o stdout &> /dev/null
./labyrinth.py -s 7 -o stdout &> /dev/null
./labyrinth.py -s 21 -o stdout &> /dev/null
./labyrinth.py -s 121 -o stdout &> /dev/null
./labyrinth.py -s 255 -o stdout &> /dev/null

# invalid sizes throw
echo "invalid parameters test"
./labyrinth.py -s 0 -o stdout &> /dev/null && err=1
./labyrinth.py -s -1 -o stdout &> /dev/null && err=1
./labyrinth.py -s 20 -o stdout &> /dev/null && err=1
./labyrinth.py -s 257 -o stdout &> /dev/null && err=1

# invalid laziness, bias and root_factor
./labyrinth.py -l 2 -o stdout &> /dev/null && err=1
./labyrinth.py -l -2 -o stdout &> /dev/null && err=1
./labyrinth.py -r -2 -o stdout &> /dev/null && err=1
./labyrinth.py -r 0 -o stdout &> /dev/null && err=1
./labyrinth.py -b 2 -o stdout &> /dev/null && err=1
./labyrinth.py -b -1.1 -o stdout &> /dev/null && err=1

# invalid color map
./labyrinth.py -c "abc" &> /dev/null && err=1

# invalid parameter type
./labyrinth.py -x -o stdout &> /dev/null && err=1


# save some formats
echo "file format test"
./labyrinth.py -o "test.png" && rm "test.png"
./labyrinth.py -o "test.pdf" && rm "test.pdf"
./labyrinth.py -o "test.jpg" && rm "test.jpg"
./labyrinth.py -o "test.jpeg" && rm "test.jpeg"
./labyrinth.py -o "test.webp" && rm "test.webp"
./labyrinth.py -o "test.svg" && rm "test.svg"

# save without ending
./labyrinth.py -o "test" && rm "test.png"

# save different sizes and bitmaps
./labyrinth.py -s 11 -o "test.png" && rm "test.png"
./labyrinth.py -s 121 -c "Greys" -o "test.png" && rm "test.png"
./labyrinth.py -s 255 -c "magma" -o "test.png" && rm "test.png"

# we don't want the images be too small or large, regardless of size setting
function check_image_size {
    image_file="$1"

    # Get the dimensions of the image using the identify command
    width=$(magick identify -format "%w" "$image_file")
    height=$(magick identify -format "%h" "$image_file")

    # Check if the dimensions are within the specified range
    if (( width < 500 || width > 1500 )) || (( height < 500 || height > 1500 )); then
        echo "Image size not in range 500-1500" >&2
    fi
}

# check image sizes
echo "image size test"
./labyrinth.py -o "test.png" && check_image_size "test.png"
./labyrinth.py -s 1 -o "test.png" && check_image_size "test.png"
./labyrinth.py -s 255 -o "test.png" && check_image_size "test.png"
rm "test.png"


# print to stderr if error flag is set
[ $err -eq 1 ] && echo "Tests failed" >&2
