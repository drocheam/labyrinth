#!/usr/bin/env python3

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt


def get_options():

    # default options
    opts = dict()
    opts["size"] = 63  # image side length
    opts["laziness"] = 0.7  # range 0-1, controls "laziness" of root direction change. Higher value leads to more straight lines.
    opts["root_factor"] = 1.3  # maximum length of one root in multiples of side length
    opts["cmap"] = "viridis"  # colormap for the pyplot
    opts["outfile"] = None  # output filename

    opts_raw, args_raw = getopt.getopt(sys.argv[1:],"s:r:l:o:c:h", [])

    for opt_raw, arg_raw in opts_raw:

        if opt_raw == "-s":
            opts["size"] = int(arg_raw)
            assert opts["size"] % 2, "size must be odd!"
            assert 0 < opts["size"] < 256, "size must be between 0 and 256"

        elif opt_raw == "-l":
            opts["laziness"] = float(arg_raw)
            assert 0 <= opts["laziness"] <= 1, "laziness must be between 0 and 1"
        
        elif opt_raw == "-r":
            opts["root_factor"] = float(arg_raw)
            assert opts["root_factor"] > 0, "root_factor should be above 0"
        
        elif opt_raw == "-o":
            opts["outfile"] = arg_raw
        
        elif opt_raw == "-c":
            opts["cmap"] = arg_raw

        elif opt_raw == "-h":
            print("Usage:")
            print("labyrinth.py [-s <side_length>] [-r <straight_ratio>] [-l <root_factor>]"
                  " [-c <colormap name>] [-o <output file>] [-h]")
            print("")
            print("-s:  size/ side length in squares. Must be odd and below 256. Default: 63")
            print("-l:  laziness in range [0, 1] defines the laziness of direction change. "
                  "A higher number leads to more straight lines. Default: 0.7")
            print("-r:  root_factor defines the maximum relative maximum length of a root the labyrinth walls consist of. "
                  "Normally this doesn't need to be adapted. Default: 1.3")
            print("-c:  colormap name for the pyplot. See the matplotlib documentation. Default: viridis")
            print("-o:  Specify a filepath string with filetype.With no output file a pyplot windows opens. "
                  "Specify '-o stdout' for terminal output. By default shows the pyplot.")
            print("-h:  print this help")
            print("")
            exit(0)


    return opts


def init_labyrinth(opts):

    # output array
    arr = np.ones((opts["size"]+6, opts["size"]+6), dtype=bool)

    # inner area is empty
    arr[3:-3, 3:-3] = 0

    # define mother root and entry + exit point
    arr[3, :-5] = 1
    arr[-4, 5:] = 1
    arr[:-5, 3] = 1
    arr[5:, -4] = 1

    return arr


def get_move_arrays(arr):
    # check if a two step move is possible in a specific direction from each position
    # 
    #  legend:     x: investigated position, must be a root     <-, ->, v-, ^-: direction arrows      
    #              o: needed empty positions                 c: center of the 3x3 box that needs to be checked
    #
    #   left                right           up             down
    #                                                        v-
    #  o o o                o o o          o o o             x
    #  o c o x  <-     -> x o c o          o c o           o o o
    #  o o o                o o o          o o o           o c o
    #                                        x             o o o
    #                                        ^-
    #   
    #  valid starting positions must lie on the following grid (valid marked by "x")
    #  x o x o x o x .
    #  o x o x o x o .
    #  x o x o x o x .
    #  ...............

    # slice array to valid area
    # only select points on valid starting grid
    arrc = arr[3:-3, 3:-3].copy()
    arrc[1::2, ::2] = False
    arrc[::2, 1::2] = False

    # check if a three element horizontal line is empty
    line_empty = lambda y0, y1, x0, x1:      (~arr[y0:y1, x0-1:x1-1]) & (~arr[y0:y1, x0:x1]) & (~arr[y0:y1, x0+1:x1+1])

    # check if a 3x3 box is empty
    box_empty = lambda y0, y1, x0, x1:      line_empty(y0-1, y1-1, x0, x1) & line_empty(y0, y1, x0, x1) & line_empty(y0+1, y1+1, x0, x1)

    # coordinate slice of the position to check (marked by x in the diagram above)
    ys, xs = arr.shape
    yc0, yc1 = 3, ys-3
    xc0, xc1 = 3, xs-3

    # create move arrays
    move_left  = arrc & box_empty( yc0,   yc1,     xc0-2, xc1-2)
    move_right = arrc & box_empty( yc0,   yc1,     xc0+2, xc1+2)
    move_up    = arrc & box_empty( yc0-2, yc1-2,   xc0,   xc1)
    move_down  = arrc & box_empty( yc0+2, yc1+2,   xc0,   xc1)

    return move_left, move_right, move_up, move_down


def grow_labyrinth(arr_p, opts):

    ind_range = np.arange(opts["size"]**2)
    N = max(1, opts["root_factor"]*opts["size"] // 2)
    
    # grow roots as long as there is space
    while 1:

        # get arrays containing valid directions at each pixel
        ml, mr, mu, md = get_move_arrays(arr_p)
        ma = ml | mr | mu | md

        # no room for roots remaining
        if not np.any(ma):
            break

        # randomly choose a root starting position where there is room to grow
        ind = np.random.choice(ind_range, p=ma.flatten()/np.count_nonzero(ma))
        iy, ix = divmod(ind, opts["size"])

        # grow a root
        for i in range(int(N)):

            # get possible move direction at current point
            ml, mr, mu, md = get_move_arrays(arr_p[iy-3+3:iy+4+3, ix-3+3:ix+4+3])
            mm = np.array([ml[0, 0], mr[0, 0], mu[0, 0], md[0, 0]])

            # no moves remaining
            if not np.any(mm):
                break

            # randomly select valid direction or in random cases go in old direction (if existing)
            if not i or not mm[mind] or np.random.sample() > opts["laziness"]:
                mind = np.random.choice(4, p=mm/np.count_nonzero(mm))

            # grow in chosen direction 
            if mind == 0:
                arr_p[iy+3, ix+1:ix+3] = 1
                ix -= 2
                
            elif mind == 1:
                arr_p[iy+3, ix+4:ix+6] = 1
                ix += 2
                
            elif mind == 2:
                arr_p[iy+1:iy+3, ix+3] = 1
                iy -= 2
                
            elif mind == 3:
                arr_p[iy+4:iy+6, ix+3] = 1
                iy += 2


def plot(arr_p, opts):

    # slice
    arr = arr_p[3:-3, 3:-3]
   
    # output to terminal
    if opts["outfile"] == "stdout":
        out = ""
        for row in arr:
            for el in row:
                out += "#I" if el else "  "
            out += "\n"
        print(out)
    
    else:
        # create figure
        plt.rcParams['toolbar'] = 'None'
        plt.figure(figsize=(6, 6))
        plt.axes().set_axis_off()
        plt.imshow(arr, cmap=opts["cmap"])
        plt.tight_layout()

        # show or save
        if opts["outfile"] is None:
            plt.show(block=True)
        else:
            plt.savefig(opts["outfile"], format=None, bbox_inches='tight', 
                        pad_inches=0, dpi=max(100, opts["size"]))


if __name__ == '__main__':

    opts = get_options()
    laby = init_labyrinth(opts)
    
    grow_labyrinth(laby, opts)
    plot(laby, opts)

