import threading
import time
from collections import deque
import random
import os

NUM_THREADS = 5
QUANTUM = 1  # segundos

db_semaphore = threading.Semaphore(2)
compiler_lock = threading.Lock()

ready_queue = deque()
thread_info = {}
thread_status = {}
status_lock = threading.Lock()
queue_lock = threading.Lock()
all_done_event = threading.Event()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_status():
    while not all_done_event.is_set():
        with status_lock, queue_lock:
            # clear_screen()
            print("=== Estado do Sistema ===")
            print("\nFila do escalonador:")
            print("→", list(ready_queue))

            print("\nThreads:")
            for tid in sorted(thread_info):
                info = thread_info[tid]
                status = thread_status.get(tid, "desconhecido")
                print(f"Thread {tid}: {status} | Tempo restante: {info['remaining']}s")

            print("\nRecursos:")
            print(f"Banco de Dados em uso: {2 - db_semaphore._value}/2")
            print(f"Compilador em uso: {'Sim' if compiler_lock.locked() else 'Não'}")
            print("\n=========================\n")
        time.sleep(0.5)

def thread_function(thread_id, total_time_needed):
    remaining_time = total_time_needed
    thread_info[thread_id]['remaining'] = remaining_time
    while remaining_time > 0:
        with queue_lock:
            if not ready_queue or ready_queue[0] != thread_id:
                thread_status[thread_id] = "esperando"
        while True:
            with queue_lock:
                if ready_queue and ready_queue[0] == thread_id:
                    ready_queue.popleft()
                    break
            time.sleep(0.05)

        thread_status[thread_id] = "tentando banco"

        got_db = db_semaphore.acquire(timeout=1)
        if not got_db:
            with queue_lock:
                ready_queue.append(thread_id)
            continue

        thread_status[thread_id] = "tentando compilador"
        got_compiler = compiler_lock.acquire(timeout=1)
        if not got_compiler:
            db_semaphore.release()
            with queue_lock:
                ready_queue.append(thread_id)
            continue

        exec_time = min(QUANTUM, remaining_time)
        thread_status[thread_id] = f"executando ({exec_time}s)"
        time.sleep(exec_time)
        remaining_time -= exec_time
        thread_info[thread_id]['remaining'] = remaining_time

        compiler_lock.release()
        db_semaphore.release()

        if remaining_time > 0:
            thread_status[thread_id] = "interrompida"
            with queue_lock:
                ready_queue.append(thread_id)
        else:
            thread_status[thread_id] = "finalizada"
            print(f"Thread {thread_id} finalizada.")

    thread_info[thread_id]['done'] = True

    if all(t['done'] for t in thread_info.values()):
        all_done_event.set()

def scheduler():
    with queue_lock:
        for tid in thread_info:
            ready_queue.append(tid)
    while not all_done_event.is_set():
        time.sleep(0.1)

def main():
    threads = []
    for i in range(NUM_THREADS):
        time_needed = random.randint(3, 7)
        thread_info[i] = {'time_needed': time_needed, 'done': False, 'remaining': time_needed}
        thread_status[i] = "pronto"
        t = threading.Thread(target=thread_function, args=(i, time_needed))
        threads.append(t)

    sched_thread = threading.Thread(target=scheduler)
    visual_thread = threading.Thread(target=show_status)

    sched_thread.start()
    visual_thread.start()

    for t in threads:
        t.start()

    for t in threads:
        t.join()
    sched_thread.join()
    visual_thread.join()

    print("✅ Todas as threads finalizaram.")

if __name__ == "__main__":
    main()
