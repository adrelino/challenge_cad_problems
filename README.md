## Overview ##
We designed an extremely simple modeling language to model a 2D sketch of horizontal and vertical lines and export them as another extremely simple B-rep representation.

For Kevin and Evan, their neural network should takes as input a B-rep file and infers the modeling language.

## The modeling language ##
Please refer to the comments in `flag.lang` for the file format.

## The B-rep file ##
Please refer to the comments in `square.brep` for the file format.

## Example ##
Run the following command to see how a modeling language is converted to a B-rep representation:
```
python model.py flag.lang
python display.py flag.brep
```

## Interactive tool ##
```
python play.py square.brep
```
