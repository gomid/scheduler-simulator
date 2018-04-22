'''
CS5250 Assignment 4, Scheduling policies simulator
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d, remaining_time %d]'%(self.id, self.arrive_time, self.burst_time, self.remaining))
    def __lt__(self, other):
        return self.remaining < other.remaining
    
def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    schedule = []
    current_time = 0
    waiting_time = 0
    completed = False
    processes = copy.deepcopy(process_list)
    running_id = -1
    
    while not completed:
        completed = True
        for process in processes:
            # skip completed process
            if process.remaining <= 0:
                continue
            
            if current_time < process.arrive_time:
                # uncompleted process exists in front
                if not completed:
                    continue
                else:
                    # move to the first future process
                    current_time = process.arrive_time
             
            if (running_id != process.id):
                schedule.append((current_time,process.id))
                running_id = process.id
            
            if process.remaining > time_quantum:
                current_time = current_time + time_quantum
                process.remaining = process.remaining - time_quantum
                completed = False
            else:
                # process is completed within this time quantum
                current_time = current_time + process.remaining
                waiting_time = waiting_time + current_time - process.arrive_time - process.burst_time
                process.remaining = 0
    
    average_waiting_time = waiting_time/float(len(processes))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    import bisect
    
    schedule = []
    working = []
    pending = copy.deepcopy(process_list)
    current_time = 0
    waiting_time = 0
    running_id = -1
    
    while working or pending:
        # add arrived process
        if pending:
            # move processes from pending to working
            for process in pending:
                if process.arrive_time == current_time:
                    bisect.insort(working, process)
                else:
                    break
            pending = [p for p in pending if p.arrive_time > current_time]
         
        if working:
            # run the front process in the working queue
            if working[0].id != running_id:
                schedule.append((current_time,working[0].id))
                running_id = working[0].id
            
            run_time = working[0].remaining
            if pending:
                run_time = min(run_time, pending[0].arrive_time - current_time)
            
            current_time = current_time + run_time
            working[0].remaining = working[0].remaining - run_time
            
            if working[0].remaining <= 0:
                # completed
                waiting_time = waiting_time + current_time - working[0].arrive_time - working[0].burst_time
                working.pop(0)       
        elif pending:
            # no process in working queue
            current_time = pending[0].arrive_time
        else:
            raise Exception('Unexpected case')
    
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SJF_scheduling(process_list, alpha):
    return (["to be completed, scheduling SJF without using information from process.burst_time"],0.0)


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
