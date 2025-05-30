import threading
import time
import random
import queue

semaforo_banco = threading.Semaphore(2)
semaforo_compilador = threading.Semaphore(1)

count = 0
tempo = 10
executando = True
algoritmo = "ROUND_ROBIN"  # Opções: FIFO, SJF, ROUND_ROBIN
quantum = 1

def safe_print(*args, **kwargs):
    if executando:
        print(*args, **kwargs)

def banco_de_dados(n, burst_time):
    global count, executando
    if not executando:
        return
    safe_print(f"{n} Está tentando acessar o banco")
    with semaforo_banco:
        safe_print(f"{n} Acessou o banco")

        with semaforo_compilador:
            safe_print(f"{n} compilando por {burst_time:.2f} segundos")
            time.sleep(burst_time)
            safe_print(f"{n} thread finalizada!")
            count += 1

        safe_print(f"{n} Liberou o banco")

def encerrar_programa():
    global executando
    executando = False
    print("\n========== TEMPO ESGOTADO ==========")
    print(f"Threads finalizadas: {count}")

timer = threading.Timer(tempo, encerrar_programa)
timer.start()

# Cria lista de tarefas com burst_time e nome
tarefas = []
for i in range(20):
    bt = random.uniform(0.5, 2.0)
    tarefas.append({'nome': f'Thread-{i+1}', 'burst': bt})

if algoritmo == "FIFO":
    fila = queue.Queue()
    for t in tarefas:
        fila.put(t)

    def worker_fifo():
        global executando
        while executando:
            try:
                t = fila.get(timeout=1)  # Espera 1 seg por tarefa
            except queue.Empty:
                break  # Sai se fila vazia por timeout
            banco_de_dados(t['nome'], t['burst'])
            fila.task_done()

    workers = []
    for _ in range(2):
        th = threading.Thread(target=worker_fifo)
        th.start()
        workers.append(th)

    for w in workers:
        w.join()

elif algoritmo == "SJF":
    fila = queue.PriorityQueue()
    for t in tarefas:
        fila.put((t['burst'], t))

    def worker_sjf():
        global executando
        while executando:
            try:
                _, t = fila.get(timeout=1)
            except queue.Empty:
                break
            banco_de_dados(t['nome'], t['burst'])
            fila.task_done()

    workers = []
    for _ in range(2):
        th = threading.Thread(target=worker_sjf)
        th.start()
        workers.append(th)

    for w in workers:
        w.join()

elif algoritmo == "ROUND_ROBIN":
    fila = queue.Queue()
    for t in tarefas:
        fila.put({'nome': t['nome'], 'restante': t['burst']})

    def worker_rr():
        global executando, count
        while executando:
            try:
                t = fila.get(timeout=1)
            except queue.Empty:
                break
            exec_time = min(quantum, t['restante'])
            safe_print(f"{t['nome']} executando por {exec_time}s (restante: {t['restante'] - exec_time:.2f}s)")
            time.sleep(exec_time)

            t['restante'] -= exec_time
            if t['restante'] > 0:
                fila.put(t)
            else:
                safe_print(f"{t['nome']} finalizada!")
                count += 1

            fila.task_done()

    workers = []
    for _ in range(2):
        th = threading.Thread(target=worker_rr)
        th.start()
        workers.append(th)

    for w in workers:
        w.join()

else:
    print("Algoritmo inválido!")

timer.cancel()
print(f"\nTotal de threads finalizadas: {count}")