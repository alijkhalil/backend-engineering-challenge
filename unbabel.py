# Import statements
import os, json, time, argparse
from datetime import datetime


# Global variables
INVALID_MIN_VAL = -1
SEC_IN_MIN = 60

INPUT_DATE_STR = "timestamp"
INPUT_DURATION_STR = "duration"

OUTPUT_DATE_STRING = "date"
OUTPUT_DURATION_STRING = "average_delivery_time"
OUTPUT_FILENAME = "running_averages.out"

# Helper functions
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

# Gets minutes from the time string of an event
def getMinFromEvent(new_event):
    time_str = new_event[INPUT_DATE_STR]
    last_min_i = time_str.rfind(':')
    final_time_str = time_str[:last_min_i]
    
    datetime_obj = datetime.strptime(final_time_str, '%Y-%m-%d %H:%M')
    return int(time.mktime(datetime_obj.timetuple()) / SEC_IN_MIN)

# Create final string representing date
def createFinalDateStr(cur_min_val):
    cur_min_val *= SEC_IN_MIN
    return datetime.fromtimestamp(cur_min_val).strftime('%Y-%m-%d %H:%M:%S')


# MinuteNode class implementation
class MinuteNode:
    def __init__(self):        
        self.num_trans = 0L
        self.total_duration = 0L
        
    def resetNode(self):
        self.num_trans = 0L
        self.total_duration = 0L
        
    def getNumTrans(self):
        return self.num_trans 
    
    def getTotalDuration(self):
        return self.total_duration 
        
    def addNewTrans(self, new_duration):
        self.num_trans += 1
        self.total_duration += new_duration
        
        
# EventCounter class implementation
class EventCounter:
    # Constructor
    def __init__(self, window_size):        
        # Check parameters
        self.window_size = window_size
        if self.window_size < 1:
           raise ValueError("The 'window_size' variable must be at least 1.")
                
        # Set up variables needed for counter ops
        self.last_index = 0
        self.last_min_val = INVALID_MIN_VAL
        
        self.running_total_trans = 0L
        self.running_total_dur = 0L
        
        self.event_history = []
        self.running_nodes = [ MinuteNode() for _ in range(self.window_size) ]
                
    # Reset counter to initial state
    def resetCounter(self):
        self.last_index = 0
        self.last_increment_val = INVALID_MIN_VAL
        
        self.running_total_trans = 0L
        self.running_total_dur = 0L
        
        self.event_history = []
        for min_node in self.running_nodes:
            min_node.resetNode()

    # Get history of running averages (over entire lifetime of counter)
    def getTransactionHistory(self):
        self.addToHistory(self.last_min_val + 1)
        tmp_history = list(self.event_history)
        self.event_history.pop()
        
        return tmp_history

    # Add the current running average to the event log
    def addToHistory(self, cur_time):
        new_record = {}
        
        avg_dur = 0.0
        if self.running_total_trans:
            avg_dur = (float(self.running_total_dur) / 
                                            float(self.running_total_trans))
        
        new_record[OUTPUT_DATE_STRING] = createFinalDateStr(cur_time)
        new_record[INPUT_DURATION_STR] = avg_dur
                                                
        self.event_history.append(new_record)
    
    # Add to internal counter variables
    def addToCounters(self, cur_min_i, cur_duration):
        self.running_total_trans += 1
        self.running_total_dur += cur_duration
        self.running_nodes[cur_min_i].addNewTrans(cur_duration)    
        
    # Remove from internal counter variables
    def removeFromCounters(self, cur_min_i):
        self.running_total_trans -= self.running_nodes[cur_min_i].getNumTrans()
        self.running_total_dur -= self.running_nodes[cur_min_i].getTotalDuration()
        self.running_nodes[cur_min_i].resetNode()    
        
    # Add new translation event
    def addTransEvent(self, new_event):
        # Get time difference between prev event and current one
        cur_min_val = getMinFromEvent(new_event)
        
        if self.last_min_val == INVALID_MIN_VAL:
            self.addToHistory(cur_min_val)
            self.last_min_val = getMinFromEvent(new_event)
        
        diff_slots = cur_min_val - self.last_min_val
        
        # Reset outdated minute counters
        if diff_slots > 0:
            cur_min_i = self.last_index
            for add_min in range(diff_slots):
                cur_min_i += 1
                
                if cur_min_i >= self.window_size:
                    cur_min_i -= self.window_size
                
                self.addToHistory(self.last_min_val + add_min + 1)
                self.removeFromCounters(cur_min_i)
            
            self.last_index = cur_min_i
        
        # Update internals with new current time
        cur_duration = new_event[INPUT_DURATION_STR]
        self.addToCounters(self.last_index, cur_duration)
    
        # Set "last seen" time to reflect this event
        self.last_min_val = cur_min_val
        
        
        
        
# Test routine    
if __name__ == '__main__':
    # Get arguments from the command line
    parser = argparse.ArgumentParser(description='Command line tool for parsing translation durations and accumulating history.')

    parser.add_argument('--input_file', type=lambda x: is_valid_file(parser, x), required=True, help='path to JSON event log file')
    parser.add_argument('--window_size', type=int, required=True, help='number representing tracking window size (in minutes)')
    
    args = parser.parse_args()
    
    # Get data and add it to the running counter
    event_data = json.load(args.input_file)
    
    tmp_counter = EventCounter(args.window_size)
    for event in event_data:
        tmp_counter.addTransEvent(event)
    
    # Dump results to a JSON file and exit program
    out_file = open(OUTPUT_FILENAME, "w")
    json.dump(tmp_counter.getTransactionHistory(), out_file) 
    out_file.close()
    
    quit()
