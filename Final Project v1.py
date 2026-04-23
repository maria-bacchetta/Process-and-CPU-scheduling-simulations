import random
from collections import deque


# Configuration

NUM_PROCESSES = 5
IO_CHANCE = 0.25


# Process States

NEW = "NEW"
READY = "READY"
RUNNING = "RUNNING"
WAITING = "WAITING"
TERMINATED = "TERMINATED"


# PCB Definition

class PCB:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.state = NEW
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time

        # Metrics
        self.start_time = -1
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = 0
    
    # Metrics Calculation
    def calculate_time(self):
        #self.turnaround_time = self.completion_time - self.arrival_time    #not used to avoid using completion time as it includes I/O block
        self.turnaround_time = self.waiting_time + self.burst_time
        #self.waiting_time = self.turnaround_time - self.burst_time         #not used because waiting is incremented
        self.response_time = self.start_time - self.arrival_time


# CPU Model

class CPU:
    def __init__(self):
        self.current = None


# Queues

job_queue = deque()
ready_queue = deque()
disk_queue = deque()
network_queue = deque()


# Logging

event_counter = 0
context_switches = 0

def log(pid, old, new, reason):
    global event_counter
    event_counter += 1
    print(f"event={event_counter} | PID={pid} | {old} -> {new} | reason={reason}")


# Process Creation

def generate_processes(NUM_PROCESSES):
    processes = []
    for i in range(NUM_PROCESSES):
        arrival_time = random.randint(0, 8)
        burst_time = random.randint(1, 5)
        p = PCB(i+1, arrival_time, burst_time)
        processes.append(p)
    
    return sorted(processes, key=lambda x: x.arrival_time) #sort by arrival time using key lambda 


# Queue and CPU initialization

cpu = CPU()
ready_queue = deque()
disk_queue = deque()
network_queue = deque()

# Table Display

def display_table(processes, title):
    print(f"\n{'='*90}")
    print(f"{title:^90}")
    print(f"{'='*90}")
    print(f"{'PID':<8} {'Arrival':<12} {'Burst':<12} {'Waiting':<12} {'Response':<12} {'Turnaround':<12} {'Completion':<12} ")
    print("-" * 90)
    
    for p in sorted(processes, key=lambda x: x.pid):
        print(f"{p.pid:<8} {p.arrival_time:<12} {p.burst_time:<12} {p.waiting_time:<12.2f} {p.response_time:<12.2f} {p.turnaround_time:<12.2f} {p.completion_time:<12.2f}")
    print(f"{'='*90}\n")

# Simulation

def simulation(all_processes):
    global current_time,context_switches
    
    display_table(all_processes, "INITIAL STATE - Before Simulation")
        
    current_time = 0
    terminated_count = 0
    cpu.current = None

    while terminated_count < NUM_PROCESSES:
        for p in all_processes:                     #process arrivals move to ready queue
            if p.arrival_time == current_time:
                old = p.state
                p.state = READY
                ready_queue.append(p)
                log(p.pid, old, READY, "process arrival")
        
        if sim_type.upper() == "SJF" and ready_queue and not (disk_queue or network_queue):     #to ensure non-preemptive scheduling
            sjf_scheduler()
        elif sim_type.upper() == "FCFS" and ready_queue and not (disk_queue or network_queue):
            fcfs_scheduler()

        if cpu.current:
            p = cpu.current
            cpu.current.remaining_time -= 1

            if cpu.current.remaining_time == 0:     #check for termination
                old = p.state
                p.state = TERMINATED
                log(p.pid, old, TERMINATED, "process finished")
                p.completion_time = current_time + 1
                p.calculate_time()
                cpu.current = None
                terminated_count += 1               #count the processes for the loop

            # Random I/O request
            elif random.random() < IO_CHANCE:
                old = p.state
                p.state = WAITING

                if random.random() < 0.5:            #add proceesses to disk or network queue
                    disk_queue.append(p)
                    log(p.pid, old, WAITING, "disk I/O request")
                else:
                    network_queue.append(p)
                    log(p.pid, old, WAITING, "network I/O request")

                cpu.current = None                       #free up the cpu

        # Disk I/O completion
        if disk_queue and random.random() < 0.3:        #process goes back to ready queue after I/O completion
            p = disk_queue.popleft()
            old = p.state
            p.state = READY
            ready_queue.append(p)
            log(p.pid, old, READY, "disk I/O complete")

        # Network I/O completion
        if network_queue and random.random() < 0.3:
            p = network_queue.popleft()
            old = p.state
            p.state = READY
            ready_queue.append(p)
            log(p.pid, old, READY, "network I/O complete")

        for p in ready_queue:                           #increment waiting time 
            p.waiting_time += 1
        
        current_time += 1

    if sim_type.upper() == "SJF":
        display_table(all_processes, "FINAL STATE - After SJF Simulation")
    elif sim_type.upper() == "FCFS":
        display_table(all_processes, "FINAL STATE - After FCFS Simulation")
    
    return all_processes

def sjf_scheduler():
    global current_time, context_switches
    if cpu.current is None and ready_queue:
        sorted_queue = sorted(ready_queue, key=lambda x: x.burst_time) #sort ready queue by burst time
        ready_queue.clear()                                             #clean ready queue
        ready_queue.extend(sorted_queue)                                #repopulate ready queue with sorted queue
        p = ready_queue.popleft()                                       #use queue because it is faster
        old = p.state                                                   #for logging purposes
        p.state = RUNNING
        cpu.current = p
        log(p.pid, old, RUNNING, "CPU dispatch")
        context_switches += 1

        if cpu.current.start_time == -1:
            cpu.current.start_time = current_time                       #used to calculate response time (start time - arrival time)

def fcfs_scheduler():
    global current_time, context_switches
    if cpu.current is None and ready_queue:
        p = ready_queue.popleft()
        old = p.state
        p.state = RUNNING
        cpu.current = p
        log(p.pid, old, RUNNING, "CPU dispatch")
        context_switches += 1

        if cpu.current.start_time == -1:
          cpu.current.start_time = current_time
    

def display_results(results):
    total_w, total_r, total_t = 0, 0, 0
    
    for p in sorted(results, key=lambda x: x.pid):
        total_w += p.waiting_time
        total_r += p.response_time
        total_t += p.turnaround_time

    print("\n" + "="*90)
    print("SIMULATION SUMMARY")
    print("="*90)
    print(f"Processes completed: {len(results)}")
    print(f"Context switches: {context_switches}")
    
    n = len(results)
    print("-" * 90)
    print(f"Average Waiting Time: {total_w/n:.2f}")
    print(f"Average Response Time: {total_r/n:.2f}")
    print(f"Average Turnaround Time: {total_t/n:.2f}")
    print("="*90 + "\n")

sim_type = input("Type SJF or FCFS for simulation type: " )
processes = generate_processes(NUM_PROCESSES)
results = simulation(processes)
display_results(results)





