# next lib
import matplotlib.pyplot as plt
import numpy as np


def graph(xlist=None, ylist=None, color=None, shw=None):
    if (xlist is None) and (ylist is None):
        print("Both lists (x list and y list) are None")
    if (xlist is None):
        xlist = []
        print("x list is None")
        for carrier in range(len(ylist)):
            xlist.append(carrier)
    if (ylist is None):
        ylist = []
        print("y list is None")
        for carrier in range(len(xlist)):
            ylist.append(carrier)
    if len(xlist) != len(ylist):
        print("Error: No x and y values passed or imbalanced lists. Pass two equally-sized arrays for x and y")
        if len(xlist) < len(ylist):#pad out the list
            for carrier in range(len(ylist)-len(xlist)):
                xlist.append(10)
        else:
            for carrier in range(len(xlist)-len(ylist)):
                ylist.append(20)
    if min(ylist) != max(ylist):
        plt.ylim(min(ylist), max(ylist))
    if min(xlist) != max(xlist):
        plt.xlim(min(xlist), max(xlist))

    xcoords = np.array(xlist)
    ycoords = np.array(ylist)
    if color is None:
        plt.plot(xcoords, ycoords, "red")
    else:
        plt.plot(xcoords, ycoords, color=color)

    if shw:
        plt.show()

def show():
    plt.show()

# lims not needed; check in generate_array_then_graph for the lims
def yrange(ylist):
   plt.ylim(min(ylist), max(ylist))
def xrange(xlist):
   plt.xlim(min(xlist), max(xlist))

def generate_array_then_graph(minimum_x=None, maximum_x=None, f=None, incrementsperunit=None, color=None,
                              show=None):  # reciprocal step can also be thought of as gradings between 0 and 1. So the gradings is 100
    max_y = -9999999999999999999999999999999999999999999999999999999999  # arbitrary small number, so that the first y value is always larger than this
    min_y = 9999999999999999999999999999999999999999999999999999999999  # arbitrary large number, so that the first y value is always smaller than this
    if str(type(minimum_x)) == "<class 'float'>":
        print("missing minimum x value to generate graph for")
        return ()
    if str(type(maximum_x)) == "<class 'float'>":
        print("missing maximum x value to generate graph for")
        return ()
    if f is None:
        print("missing function to generate graph for")
        return ()
    if incrementsperunit is None or incrementsperunit < 1:  # plan is to make parametric using carrier as t and then passing equation of x through
        print("setting default increments per unit to 1")
        incrementsperunit = 1
    min_x = minimum_x
    max_x = maximum_x
    reciprocal_step = incrementsperunit  # so this is a step of 0.01 if reciprocal_step=100

    # data generation
    # cartesian only
    coords_x = []
    coords_y = []

    # first generate and plot x-axis, can be generated beforehand as we have all x values before we have all y values
    # but don't show the plot yet
    x_axis(min_x, max_x)

    for carrier in range((min_x * reciprocal_step), (max_x * reciprocal_step) + 1,
                         1):  # +1 as the last value is not reached (start, iterations, step)
        # print(carrier)
        x = carrier / reciprocal_step
        coords_x.append(x)
        # merged loops together to perform quicker time
        y = f(x)
        if y > max_y:
            max_y = y
        if y < min_y:
            min_y = y
        coords_y.append(y)  # inside of bracket is the equation

    # second, generate y-axis, has to be generated after all y values are generated, as we need to know the min and max y values to draw the y axis
    # still don't show the plot yet
    y_axis(min_y, max_y)

    # yrange(coords_y)
    # xrange(coords_x)

    # then finally graph f(x) and use the show flag the user gave
    graph(coords_x, coords_y, color, show)

#does not need to be called manually, so it is not provided in package
def x_axis(minimum_x, maximum_x):  # needed for x axis, do not change
    graph([minimum_x, maximum_x], [0, 0], "black", False)  # do not change this, either. Gives y=0 to draw the x axis

#does not need to be called manually, so it is not provided in package
def y_axis(minimum_y, maximum_y):  # needed for y axis, do not change
    graph([0, 0], [minimum_y, maximum_y], "black", False)  # do not change this, either. Gives x=0 to draw the y axis


def parametric_graph():
    print("Behind the scenes... NOT FINISHED CRTL+C THIS RN")


def test():
    print("program is present and is running--END OF TEST")

