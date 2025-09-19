from main import *
import math
from math import *
#how to use:
#create function with param x=None. Then return what you want the function of x, or y to be
#use generate_array_then_graph to use a function of x to define and create graph
#use graph to pass two, equally-sized arrays as arguments to function

list1=[]
list2=[]

for carrier in range(7):
    for carrier2 in range(7):
        list1.append(carrier*carrier2)

for carrier in range(49):
    list2.append(carrier)


def f(x=None):
    return(x**2)#equation of y in terms of x should be put here


def x_axis(x=None): # needed for x axis, do not change
    return(0) #do not change this, either. Gives y=0 to draw the x axis


def g(x=None):
    return(sin((2*math.pi*x)/720))#equation of y in terms of x should be put here


#graph.graph([0,0],[-100000,100000],"black",False) #y axis
generate_array_then_graph(-100000,100000,f,1,"black",True) # defining x axis
generate_array_then_graph(-1000,1000,g,1000,"blue",False)
#graph.generate_array_then_graph(-1000,1000,f,100,"green",True)


#graph.graph(list2,list1,"black",True)#use this if you already have an array of values for x and y (equal length) to graph
