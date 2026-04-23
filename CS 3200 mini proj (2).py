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

class PCB:
    def __init__(self, pid, work_units):
        self.pid = pid
        self.state = NEW
        self.program_counter = 0
        self.remaining_work = work_units
        self.remaining_io = 0


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

for i in range(1, NUM_PROCESSES + 1):
    work = random.randint(5, MAX_WORK_UNITS)
    p = PCB(i, work)
    job_queue.append(p)

# Admit all processes
while job_queue:
    p = job_queue.popleft()
    old = p.state
    p.state = READY
    ready_queue.append(p)
    log(p.pid, old, READY, "system admission")


# Simulation

cpu = CPU()
terminated_count = 0

while terminated_count < NUM_PROCESSES:

    if cpu.current is None and ready_queue:
        p = ready_queue.popleft()
        old = p.state
        p.state = RUNNING
        cpu.current = p
        log(p.pid, old, RUNNING, "CPU dispatch")
        context_switches += 1

    if cpu.current:
        p = cpu.current
        p.program_counter += 1
        p.remaining_work -= 1

        # Check termination
        if p.remaining_work <= 0:
            old = p.state
            p.state = TERMINATED
            log(p.pid, old, TERMINATED, "process finished")
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

    print_queues(cpu)


# Simulation Summary

print("\nSIMULATION COMPLETE")
print("Processes completed:", terminated_count)
print("Context switches:", context_switches)







