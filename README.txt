Skotheim Ilastik Pipeline current status:

12/11/2017: Put on hiatus per JMS's instructions.

Architecture of current code:

Ilastik tracking exports the tracked cells in two formats: a color-coded TIFF image mask and a CSV file.
The image colors are according to the cell's LINEAGE: that is, the label of the cell's earliest ancestor.
The image does not carry any information to distinguish daughter 1A from daughter 1B from mother 1.

The CSV file contains this important information. The CSV is organized with one row per cell per timepoint, with columns
indicating plenty of data about the cell: its 'LabelID' (a randomly assigned number applicable to the given timepoint only),
its 'TrackId' (a number assigned at the cell's birth, and the number used as the basis for understanding the tracks), its
'LineageId' (the lineage explained above), its location coordinates, area, intensity measurements, etc.

The first thing the pipeline does is to convert the CSV to a more user-friendly DataFrame structure, using the
method 'convertIlastikCSV'. This produces a DataFrame with a simple row-wise index corresponding to the timepoints
and a hierarchical column-wise index: the top level is the 'cell number' (equivalent to TrackId) and the lower level
is the 'measurement' which stores the appropriate data about that cell at that timepoint.

(A complementary program exists in the DataFrameFromImage, DataFrameFromImage_Main, and relabelManualTrack modules.
These were built to interact with the image produced by ilastik and construct an equivalent DataFrame structure,
but do not contain a lot of the essential information that is missing from the ilastik images, as discussed above.)

The dataframe_utils module contains some methods for working with DataFrames.

One of the goals of this project was to enable editing of ilastik-derived tracks by requesting user input through a simple GUI.
To do this, the Experiment class was created. Its constructor method begins by calling the convertIlastikCSV method to create
a DataFrame that contains all the necessary data.

An Experiment object is created for a given experiment (i.e., a given raw image and associated ilastik CSV output).
The Experiment object contains a Series of objects of the Track class. Each Track object was designed to correspond
to a single cell's lifetime of tracking information. The Experiment constructor also recreates a DataFrame from these
Tracks to confirm that the lineage was constructed properly. The complex object-oriented data structure in an Experiment
is saved by pickling.

The Track object for a cell that exists for n frames consists of n linked TrackPoint objects, each corresponding
to the cell's existence at a single timepoint. Each TrackPoint object contains information about the cell at that time
as well as pointers to the previous and next TrackPoints (or mother and daughter TrackPoints in the case of a dividing cell.)
A new Track creates an initial TrackPoint, then propagates it through time recursively.

The above data structure needs some tweaking but is generally satisfactory.

The most recent area being addressed is a simple GUI to allow user input to fix problematic tracks. The TrackGUI class
implements a basic version of this. It is generated for a small image region and slice out of the larger image stack,
and displays one frame of this small stack at a time. It listens for keyboard and mouse input and updates the displayed image accordingly.
It can currently scroll through the stack and identify which cell is clicked on. It is not yet competent to adjust track linkages
based on user clicks.

Major areas of necessary future development:
Identify likely troublesome tracking hotspots from the ilastik output. Might want to consider big jumps in intensity, area, or position;
may also desire user input at all division events.
Adjust track linkages based on user clicks.
Generate relevant plots from the tracks, such as G1 length vs birth size.
Handle more than one image stack, with more than two colors.

To be continued...
