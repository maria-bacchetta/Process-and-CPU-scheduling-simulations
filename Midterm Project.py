import random
from collections import deque


# Configuration

NUM_PROCESSES = 10
IO_CHANCE = 0.25
MAX_WORK_UNITS = 10


# Process States

NEW = "NEW"
READY = "READY"
RUNNING = "RUNNING"
WAITING = "WAITING"
TERMINATED = "TERMINATED"


# PCB Definition

remaining_time = 0
start_time = 0
completion_time = 0

class PCB:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.state = NEW
        self.program_counter = 0
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        #self.priority = priority
        self.remaining_time = burst_time

        # Metrics
        self.start_time = -1
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = 0
    
    # Metrics Calculation
    def calculate_time(self):
        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time
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


# Queue Snapshot

def print_queues(cpu):
    print("\n--- QUEUE SNAPSHOT ---")

    print("Ready Queue:", [p.pid for p in ready_queue])
    print("Disk Queue:", [p.pid for p in disk_queue])
    print("Network Queue:", [p.pid for p in network_queue])

    if cpu.current:
        print("CPU:", cpu.current.pid)
    else:
        print("CPU: idle")

    print("----------------------\n")


# Process Creation

def generate_processes(NUM_PROCESSES):
    for i in range(NUM_PROCESSES):
        #work = random.randint(5, MAX_WORK_UNITS)
        arrival_time = random.randint(0, 10)
        burst_time = random.randint(1, 5)
        #priority = random.randint(1, 5)
        p = PCB(i+1, arrival_time, burst_time)
        job_queue.append(p)

    #sort by arrival time
    return sorted(job_queue, key=lambda x: x.arrival_time)



# Admit all processes

while job_queue:
    p = job_queue.popleft()
    old = p.state
    p.state = READY
    ready_queue.append(p)
    log(p.pid, old, READY, "system admission")

# Simulation

cpu = CPU()
ready_queue = deque()
disk_queue = deque()
network_queue = deque()
job_queue = deque()
terminated_count = 0
current_time = 0

# Shortest Job First

def simulation(NUM_PROCESSES):
    global context_switches
    all_processes = []
    for i in range(NUM_PROCESSES):
        arrival_time = random.randint(0, 10)
        burst_time = random.randint(1, 10)
        #priority = random.randint(1, 5)
        p = PCB(i+1, arrival_time, burst_time)
        all_processes.append(p)

    current_time = 0
    terminated_count = 0
    #finished_processes = []
    cpu.current = None

    while terminated_count < NUM_PROCESSES:
        # Check for arrivals
        for p in all_processes:
            if p.arrival_time == current_time:
                old = p.state
                p.state = READY
                ready_queue.append(p)
                log(p.pid, old, READY, "process arrival")
        
        # SJF logic
        if cpu.current is None and ready_queue:
            sorted_queue = sorted(ready_queue, key=lambda x: x.burst_time)
            ready_queue.clear()
            ready_queue.extend(sorted_queue)
            p = ready_queue.popleft()
            old = p.state
            p.state = RUNNING
            cpu.current = p
            log(p.pid, old, RUNNING, "CPU dispatch")
            context_switches += 1

            if cpu.current.start_time == -1:
                cpu.current.start_time = current_time

        if cpu.current:
            p = cpu.current
            p.program_counter += 1
            cpu.current.remaining_time -= 1

            # Check termination
            if cpu.current.remaining_time == 0:
                old = p.state
                p.state = TERMINATED
                log(p.pid, old, TERMINATED, "process finished")
                p.completion_time = current_time
                p.calculate_time()
                cpu.current = None
                terminated_count += 1

            # Random I/O request
            elif random.random() < IO_CHANCE:
                old = p.state
                p.state = WAITING

                if random.random() < 0.5:
                    disk_queue.append(p)
                    log(p.pid, old, WAITING, "disk I/O request")
                else:
                    network_queue.append(p)
                    log(p.pid, old, WAITING, "network I/O request")

                cpu.current = None

        # Disk I/O completion
        if disk_queue and random.random() < 0.3:
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

        current_time += 1

    return all_processes

def display_results(results):
    print("\n" + "="*70)
    print(f"{'PID':<5} {'Arrival':<10} {'Burst':<10} {'Wait':<10} {'Resp':<10} {'Turn':<10} {'Comp':<10}")
    print("-" * 70)
    
    total_w, total_r, total_t = 0, 0, 0
    
    # Sort by PID for the final display table
    for p in sorted(results, key=lambda x: x.pid):
        print(f"{p.pid:<5} {p.arrival_time:<10} {p.burst_time:<10} {p.waiting_time:<10} "
              f"{p.response_time:<10} {p.turnaround_time:<10} {p.completion_time:<10}")
        
        total_w += p.waiting_time
        total_r += p.response_time
        total_t += p.turnaround_time

    print("\nSIMULATION COMPLETE")
    print("Processes completed:", terminated_count)
    print("Context switches:", context_switches)

    n = len(results)
    print("-" * 70)
    print(f"AVERAGES:  Waiting: {total_w/n:.2f} | Response: {total_r/n:.2f} | Turnaround: {total_t/n:.2f}")
    print("="*70 + "\n")

simulation(5)





