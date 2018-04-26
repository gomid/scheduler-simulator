'''
CS5250 Assignment 4, Scheduling policies simulator
Author: Minh Ho
Author: Qijia Wang
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

class Process:
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d, remaining_time %d]'%(self.id, self.arrive_time, self.burst_time, self.remaining))
    def __lt__(self, other):
        if self.id == other.id:
            return self.arrive_time < other.arrive_time
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
    run_id = -1
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
            if (run_id != process.id): 
                schedule.append((current_time,process.id))
                run_id = process.id
            
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
    pending = []
    processes = copy.deepcopy(process_list)
    current_time = 0
    waiting_time = 0
    running_id = -1
    
    while pending or processes:
        # add arrived process
        if processes:
            # move processes to pending queue
            for process in processes:
                if process.arrive_time == current_time:
                    bisect.insort(pending, process)
                else:
                    break
            processes = [p for p in processes if p.arrive_time > current_time]
         
        if pending:
            # run the front process in the working queue
            if pending[0].id != running_id:
                schedule.append((current_time,pending[0].id))
                running_id = pending[0].id
            
            run_time = pending[0].remaining
            if processes:
                run_time = min(run_time, processes[0].arrive_time - current_time)
            
            current_time = current_time + run_time
            pending[0].remaining = pending[0].remaining - run_time
            
            if pending[0].remaining <= 0:
                # completed
                waiting_time = waiting_time + current_time - pending[0].arrive_time - pending[0].burst_time
                pending.pop(0)       
        elif processes:
            # no process in working queue
            current_time = processes[0].arrive_time
        else:
            raise Exception('Unexpected case')
    
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

# SJF with predition
def SJF_scheduling(process_list, alpha):
    INIT_PREDICTION = 5
    predictions = {p.id:INIT_PREDICTION for p in process_list}
    
    schedule = []
    current_time = 0
    waiting_time = 0
    pending = []
    idx = 0
    
    while idx < len(process_list) or pending:
        # add arrived processes to pending
        while idx < len(process_list) and process_list[idx].arrive_time <= current_time:
            pending.append(process_list[idx])
            idx = idx + 1

        if pending:
            # pick one process from pending
            shortest = pending[0]
            for process in pending:
                if predictions[process.id] < predictions[shortest.id]:
                    shortest = process
           
            schedule.append((current_time,shortest.id))
            waiting_time = waiting_time + current_time - shortest.arrive_time
            current_time = current_time + shortest.burst_time
            predictions[shortest.id] = predictions[shortest.id] * (1 - alpha) + shortest.burst_time * alpha
            pending.remove(shortest)
        elif idx < len(process_list):
            current_time = process_list[idx].arrive_time
        else:
            raise Exception('Unexpected case')
            
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


def read_input(input_file):
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


def task_1():
    input_file = 'input.txt'
    process_list = read_input(input_file)
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
    

def task_2():
    input_file = 'input2.txt'
    process_list = read_input(input_file)
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list, 2)
    write_output('RR2.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, 0.5)
    write_output('SJF2.txt', SJF_schedule, SJF_avg_waiting_time )

    for quantum in range(1, 13, 1):
        _, RR_avg_waiting_time =  RR_scheduling(process_list, quantum)
        with open('RR_quantum.csv', 'a') as f:
            f.write('%d,%.2f\n'%(quantum, RR_avg_waiting_time))
    for i in range(1, 10, 1):
        _, SJF_avg_waiting_time =  SJF_scheduling(process_list, i*0.1)
        with open('SJF_alpha.csv', 'a') as f:
            f.write('%f,%.2f\n'%(i*0.1, SJF_avg_waiting_time))


def main(argv):
    task_2()
    

if __name__ == '__main__':
    main(sys.argv[1:])
