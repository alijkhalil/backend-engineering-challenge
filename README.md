This file should be read in conjunction with the implementation for my running event 
counter program -- "unbabel.py" -- in this repo.  It will describe my solution at a high 
level and also explain each component in detail.

To start, there are several global variables and helper functions.  These functions 
each perform some kind of problem-specific validation or conversion.  More specifically, 
there is method for ensuring that the command line path to the input file is valid.  
Next, you will find a function taking an event object and returning its minute value 
(using its timestamp string).  And lastly, there is a function to create the date string 
(from a minute value) for the output log.

Further in the solution, you will find the MinuteNode class.  It is very basic and 
contains two member variables.  One represents the number of transactions and the other 
tracks the total duration of the transactions for that minute.  It also has a member 
functions for adding a new event/transaction to the node and resetting both member variables 
back to zero.

As the core of the implementation, I have included the EventCounter class.  It keeps track 
of the running totals for the number of events and their total duration over the window size 
using a circular array of MinuteNode objects.  Each MinuteNode object in the array corresponds 
to a minute in the last X minutes (where X is the window size).  As its principle function, 
the class uses "addTransEvent" to add new events to the counter.  In this method, it first 
determines the difference in minutes between the current event and the last added event.  If 
the difference is zero, then it simply increments its internal counter variables for the 
number of events and total duration in the current MinuteNode.  However, when the time 
difference between the last two events is larger than zero, it decrements the EventCounter's 
counters by the values in the MinuteNode objects now falling outside the time window and 
resets the internal counter variables in those MinuteNode objects.  Additionally, as time 
elaspes, the EventCounter will keep running averages for each passing minute in its 
"event_history" variable using the "addToHistory" function.

Finally, in the main routine, you will find the command line parser so that the program can 
accept an input event log file and running window size.  After the file path is verified and 
opened, the program will create an EventCounter object (corresponding to the correct window 
size) and pass each event to it.  As the final step, it will output the running average 
history to a file called "running_averages.out".