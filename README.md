## Overview ##
An extremely simple modeling language to model a 2D sketch of horizontal and vertical lines and export them as another extremely simple B-rep representation.

## The modeling language ##
Please refer to the comments in `flag.lang` for the file format.

## The B-rep file ##
Please refer to the comments in `flag.brep` for the file format.

## Example ##
Run the following command to see how a modeling language is converted to a B-rep representation:
```
python model.py flag.lang
```

## Interactive tool ##
```
python play.py flag.brep
```

## Your Task ##

### Step 0
First, get a feel of what the iCAD system does by trying to figure out how to reconstruct the flag by issueing a series of commands in the interpreter
```
python play.py flag.brep
```
Each intermediate step is drawn into haha.png so if you have it open, you will see it updates over time as you add more commands

### Step 1
The first programming task is to refactor the code. In model.py to
use an abstract syntax tree (AST) for each of the commands that you would type into
play.py, for instance, vertex, hline, and vline (more if needed) you have to figure out what is the best way to represent these, we don't have skeleton code for you here.

Second, implement a parser that takes in the strings typed into play.py into
these classesyou just defined, do this code under model.py under parse\_command

Third, modify execute\_command under model.py so that you can take as input the AST returned by your parse\_command method

if you search for "TODO" under
play.py and model.py you will see where your code should go

you are successful if a) you can still run play.py on flag.brep, and b) your refactor looks clean

### Step 2 
Add support for an arc primitive as a new AST node defined by (x,y,r,theta\_start, theta\_end)

Able to interactively draw a curvy flag shown in curveflag.png demo


