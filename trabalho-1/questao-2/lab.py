import threading
import time
import random

# Recursos
compilador_lock = threading.Lock()
banco_dados_semaforo = threading.Semaphore(2)

# Parâmetros
T1, T2 = 1, 3    # burst curto
T3, T4 = 5, 8    # burst longo
NUM_PROCESSOS = 6
QUANTUM = 1.0    # só usado no RR

class Processo:
    def __init__(self, nome, burst_time):
        self.nome = nome
        self.burst_time_total = burst_time
        self.burst_time_restante = burst_time
        self.compilado = False

    def compilar(self, tempo):
        tempo_exec = min(self.burst_time_restante, tempo)

        banco_dados_semaforo.acquire()
        compilador_lock.acquire()

        print(f"[{self.nome}] INICIO compilar por {tempo_exec:.2f}s (restante {self.burst_time_restante:.2f}s)")
        time.sleep(tempo_exec)  # Simula compilação
        self.burst_time_restante -= tempo_exec
        print(f"[{self.nome}] FIM compilar, resto {self.burst_time_restante:.2f}s")

        compilador_lock.release()
        banco_dados_semaforo.release()

        if self.burst_time_restante <= 0:
            self.compilado = True

        return tempo_exec

    def pensar(self):
        think_time = random.uniform(1, 2)
        print(f"[{self.nome}] Pensando por {think_time:.2f}s...")
        time.sleep(think_time)

# Escalonadores

def escalonador_rr(processos, quantum):
    from collections import deque
    fila = deque(processos)

    while fila:
        processo = fila.popleft()
        if processo.compilado:
            print(f"[{processo.nome}] Processo já compilado, removendo da fila.")
            continue

        tempo_usado = processo.compilar(quantum)

        if not processo.compilado:
            processo.pensar()
            fila.append(processo)
        else:
            print(f"[{processo.nome}] Processo FINALIZADO.")

def escalonador_fcfs(processos):
    # FCFS sem preempção, processo executa todo burst de uma vez
    for processo in processos:
        if processo.compilado:
            continue
        print(f"\n[{processo.nome}] Iniciando FCFS")
        processo.compilar(processo.burst_time_restante)
        processo.pensar()
        print(f"[{processo.nome}] Processo FINALIZADO.")

def escalonador_sjf(processos):
    # SJF não preemptivo: ordena pela burst time total
    processos_ordenados = sorted(processos, key=lambda p: p.burst_time_total)

    for processo in processos_ordenados:
        if processo.compilado:
            continue
        print(f"\n[{processo.nome}] Iniciando SJF")
        processo.compilar(processo.burst_time_restante)
        processo.pensar()
        print(f"[{processo.nome}] Processo FINALIZADO.")

if __name__ == "__main__":
    # Criar processos: metade com burst curto, metade longo
    processos_rr = []
    processos_fcfs = []
    processos_sjf = []
    for i in range(NUM_PROCESSOS):
        if i < NUM_PROCESSOS // 2:
            burst = random.uniform(T1, T2)
        else:
            burst = random.uniform(T3, T4)

        # Criar cópias para cada escalonador independente
        processos_rr.append(Processo(f"RR-Processo-{i+1}", burst))
        processos_fcfs.append(Processo(f"FCFS-Processo-{i+1}", burst))
        processos_sjf.append(Processo(f"SJF-Processo-{i+1}", burst))

    print("\n==== Escalonador Round Robin ====")
    escalonador_rr(processos_rr, QUANTUM)

    print("\n==== Escalonador FCFS ====")
    escalonador_fcfs(processos_fcfs)

    print("\n==== Escalonador SJF ====")
    escalonador_sjf(processos_sjf)

    print("\nTodos os processos finalizaram.")
