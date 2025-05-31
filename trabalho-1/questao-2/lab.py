import threading
import time
import random

semaforo_banco = threading.Semaphore(2)
semaforo_compilador = threading.Semaphore(1)

tempo = 20   
count = 0
executando = True

def banco_de_dados(nome, burst):
    global count, executando
    safe_print(f"{nome} Está tentando acessar o banco")
    with semaforo_banco:
        safe_print(f"{nome} Acessou o banco")
        
        with semaforo_compilador:
            safe_print(f"{nome} compilando...")
            time.sleep(burst)
            safe_print(f"{nome} thread finalizada!")
    
        time.sleep(1)
        safe_print(f"{nome} Liberou o banco")
        count += 1

def encerrar_programa():
        global executando
        executando = False
        print("\n========== TEMPO ESGOTADO ==========")
        print(f"Threads finalizadas: {count}")

def safe_print(*args, **kwargs):
    if executando:
        print(*args, **kwargs)

timer = threading.Timer(tempo, encerrar_programa)
timer.start()

threads = []

for i in range(20):
    nome = f"Thread-{i+1}"
    burst = random.uniform(0.5, 2.0) 

    t = threading.Thread(target=banco_de_dados, args=(nome, burst))
    threads.append(t)
    t.start()
for t in threads:   
    t.join()