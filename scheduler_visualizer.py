import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

# Function to calculate completion, turnaround, and waiting times
def calculate_times(processes, gantt_chart):
    completion_times = {}
    turnaround_times = {}
    waiting_times = {}

    # Calculate Completion Time
    for process_id, start, end in gantt_chart:
        completion_times[process_id] = end

    # Calculate Turnaround Time (Completion Time - Arrival Time)
    for process_id, arrival, _ in processes:
        turnaround_times[process_id] = completion_times[process_id] - arrival

    # Calculate Waiting Time (Turnaround Time - Burst Time)
    for process_id, _, burst in processes:
        waiting_times[process_id] = turnaround_times[process_id] - burst

    return completion_times, turnaround_times, waiting_times


# First-Come-First-Serve (FCFS) Scheduling Algorithm
def fcfs(processes):
    processes.sort(key=lambda x: x[1])  # Sort by arrival time
    time = 0
    gantt_chart = []

    for process_id, arrival, burst in processes:
        start_time = max(time, arrival)
        end_time = start_time + burst
        gantt_chart.append((process_id, start_time, end_time))
        time = end_time

    return gantt_chart


# Shortest Job First (Non-Preemptive) Scheduling Algorithm
def sjf(processes):
    processes.sort(key=lambda x: (x[1], x[2]))  # Sort by arrival time, then burst time
    ready_queue = []
    time = 0
    gantt_chart = []

    while processes or ready_queue:
        # Add processes to the ready queue whose arrival time <= current time
        while processes and processes[0][1] <= time:
            ready_queue.append(processes.pop(0))

        if ready_queue:
            # Sort ready queue by burst time
            ready_queue.sort(key=lambda x: x[2])
            process_id, arrival, burst = ready_queue.pop(0)
            start_time = max(time, arrival)
            end_time = start_time + burst
            gantt_chart.append((process_id, start_time, end_time))
            time = end_time
        else:
            time = processes[0][1]  # Jump to the next process's arrival time

    return gantt_chart


# Shortest Job First (Preemptive) Scheduling Algorithm
def preemptive_sjf(processes):
    processes.sort(key=lambda x: x[1])  # Sort by arrival time
    time = 0
    gantt_chart = []
    ready_queue = []
    ongoing_process = None
    remaining_times = {pid: burst for pid, _, burst in processes}

    while processes or ready_queue or ongoing_process:
        # Add processes to the ready queue whose arrival time <= current time
        while processes and processes[0][1] <= time:
            ready_queue.append(processes.pop(0))

        if ongoing_process:
            ready_queue.append(ongoing_process)

        if ready_queue:
            # Sort ready queue by burst time
            ready_queue.sort(key=lambda x: remaining_times[x[0]])
            ongoing_process = ready_queue.pop(0)

            # Execute the current process for 1 unit of time
            pid, arrival, _ = ongoing_process
            remaining_times[pid] -= 1
            gantt_chart.append((pid, time, time + 1))

            if remaining_times[pid] == 0:
                ongoing_process = None
            time += 1
        else:
            time = processes[0][1]  # Jump to the next process's arrival time

    # Merge consecutive intervals of the same process for a cleaner Gantt chart
    merged_gantt = []
    for process_id, start, end in gantt_chart:
        if merged_gantt and merged_gantt[-1][0] == process_id:
            merged_gantt[-1] = (process_id, merged_gantt[-1][1], end)
        else:
            merged_gantt.append((process_id, start, end))

    return merged_gantt


# Round Robin Scheduling Algorithm
def round_robin(processes, quantum):
    # Sort processes by arrival time
    processes.sort(key=lambda x: x[1])
    ready_queue = []
    time = 0
    gantt_chart = []
    remaining_times = {pid: burst for pid, _, burst in processes}

    while processes or ready_queue:
        # Add processes to the ready queue whose arrival time <= current time
        while processes and processes[0][1] <= time:
            ready_queue.append(processes.pop(0))

        if ready_queue:
            process_id, arrival, burst = ready_queue.pop(0)
            start_time = max(time, arrival)

            # Process for up to quantum time
            execute_time = min(remaining_times[process_id], quantum)
            end_time = start_time + execute_time
            gantt_chart.append((process_id, start_time, end_time))

            remaining_times[process_id] -= execute_time
            time = end_time

            # If the process still needs more time, add it back to the ready queue
            if remaining_times[process_id] > 0:
                ready_queue.append((process_id, arrival, remaining_times[process_id]))

        else:
            # Jump to the next process's arrival time if no process is in the ready queue
            time = processes[0][1]

    return gantt_chart


# Plot Gantt Chart
def plot_gantt_chart(gantt_chart):
    fig, ax = plt.subplots(figsize=(10, 6))

    for idx, (process_id, start, end) in enumerate(gantt_chart):
        ax.barh(y=0, width=end - start, left=start, height=0.5, edgecolor='black', align='center')
        ax.text((start + end) / 2, 0, process_id, ha='center', va='center', color='white', fontweight='bold')

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("Gantt Chart")
    plt.show()


# Simulate Button Action
def simulate_and_plot():
    try:
        quantum = None
        if algorithm.get() == "Round Robin":
            quantum = int(quantum_entry.get())

        processes = []
        for process_entry in process_entries:
            pid, arrival, burst = process_entry
            processes.append((pid.get(), int(arrival.get()), int(burst.get())))

        if algorithm.get() == "FCFS":
            gantt_chart = fcfs(processes)
        elif algorithm.get() == "SJF":
            gantt_chart = sjf(processes)
        elif algorithm.get() == "Preemptive SJF":
            gantt_chart = preemptive_sjf(processes)
        elif algorithm.get() == "Round Robin":
            gantt_chart = round_robin(processes, quantum)

        # Calculate Completion, Turnaround, and Waiting Times
        completion_times, turnaround_times, waiting_times = calculate_times(processes, gantt_chart)

        # Display the table
        display_process_table(processes, completion_times, turnaround_times, waiting_times)

        plot_gantt_chart(gantt_chart)

    except ValueError:
        result_label.config(text="Invalid input! Please enter valid numbers.")


# Display Process Table
def display_process_table(processes, completion_times, turnaround_times, waiting_times):
    for row in process_table.get_children():
        process_table.delete(row)

    for process_id, arrival, burst in processes:
        completion_time = completion_times[process_id]
        turnaround_time = turnaround_times[process_id]
        waiting_time = waiting_times[process_id]
        process_table.insert("", "end", values=(process_id, arrival, burst, completion_time, turnaround_time, waiting_time))


# Add Process Row
def add_process_row():
    pid = tk.StringVar(value=f"P{len(process_entries) + 1}")
    arrival = tk.StringVar()
    burst = tk.StringVar()

    pid_entry = ttk.Entry(frame, textvariable=pid, width=5)
    arrival_entry = ttk.Entry(frame, textvariable=arrival, width=5)
    burst_entry = ttk.Entry(frame, textvariable=burst, width=5)

    pid_entry.grid(row=len(process_entries) + 1, column=0)
    arrival_entry.grid(row=len(process_entries) + 1, column=1)
    burst_entry.grid(row=len(process_entries) + 1, column=2)

    process_entries.append((pid, arrival, burst))


# GUI Setup
root = tk.Tk()
root.title("Scheduling Algorithm Visualizer")
frame = ttk.Frame(root, padding=10)
frame.grid()

# Headers
ttk.Label(frame, text="Process ID").grid(row=0, column=0)
ttk.Label(frame, text="Arrival Time").grid(row=0, column=1)
ttk.Label(frame, text="Burst Time").grid(row=0, column=2)

process_entries = []
add_process_row()

# Add Process Button
add_button = ttk.Button(frame, text="Add Process", command=add_process_row)
add_button.grid(row=100, column=0, pady=10)

# Algorithm Dropdown
ttk.Label(frame, text="Algorithm").grid(row=101, column=0)
algorithm = ttk.Combobox(frame, values=["FCFS", "SJF", "Preemptive SJF", "Round Robin"])
algorithm.grid(row=101, column=1)
algorithm.set("FCFS")

# Quantum Input
ttk.Label(frame, text="Time Quantum").grid(row=102, column=0)
quantum_entry = ttk.Entry(frame)
quantum_entry.grid(row=102, column=1)

# Simulate Button
simulate_button = ttk.Button(frame, text="Simulate", command=simulate_and_plot)
simulate_button.grid(row=103, column=0, pady=10)

# Result Label
result_label = ttk.Label(frame, text="")
result_label.grid(row=104, column=0, columnspan=3)

# Table for process details
process_table = ttk.Treeview(root, columns=("Process ID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time"))
process_table.grid(row=1, column=0, padx=10, pady=10)
process_table.heading("Process ID", text="Process ID")
process_table.heading("Arrival Time", text="Arrival Time")
process_table.heading("Burst Time", text="Burst Time")
process_table.heading("Completion Time", text="Completion Time")
process_table.heading("Turnaround Time", text="Turnaround Time")
process_table.heading("Waiting Time", text="Waiting Time")
process_table["show"] = "headings"

root.mainloop()
