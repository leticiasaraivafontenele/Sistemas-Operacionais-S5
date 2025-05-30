import threading
import time
import random

class Processo(threading.Thread):
    def __init__(self, id, burst_time):
        super().__init__()
        self.id = id
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.end_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.executed_time = 0
        self.lock = threading.Lock()

    def run(self):
        # Aguarda o escalonador liberar
        while self.remaining_time > 0:
            time.sleep(0.01)  # Espera ativa para evitar sair da thread

def round_robin(processos, quantum):
    time_elapsed = 0
    queue = processos[:]

    print("\n--- Iniciando escalonamento Round Robin ---\n")

    while any(p.remaining_time > 0 for p in processos):
        for processo in queue:
            if processo.remaining_time <= 0:
                continue

            exec_time = min(quantum, processo.remaining_time)

            if processo.start_time is None:
                processo.start_time = time_elapsed

            print(f"[t={time_elapsed}s] Executando P{processo.id} por {exec_time}s")

            time.sleep(exec_time * 0.1)  # Simula o tempo de execução real (ajustável)
            processo.remaining_time -= exec_time
            processo.executed_time += exec_time
            time_elapsed += exec_time

            if processo.remaining_time == 0:
                processo.end_time = time_elapsed
                processo.turnaround_time = processo.end_time
                processo.waiting_time = processo.end_time - processo.burst_time
                print(f"[t={time_elapsed}s] P{processo.id} finalizado.")

def main(quantum, num_processos):
    # Gera burst times aleatórios entre 5 e 15
    processos = [Processo(id=i+1, burst_time=random.randint(5, 15)) for i in range(num_processos)]

    # Inicia todas as threads (em estado "ativo", mas a execução real é controlada pelo escalonador)
    for p in processos:
        p.start()

    round_robin(processos, quantum)

    for p in processos:
        p.join()

    print("\n--- Resultados ---")
    total_wait = 0
    total_turnaround = 0
    for p in processos:
        print(f"Processo P{p.id} | Burst Time: {p.burst_time} | Espera: {p.waiting_time} | Retorno: {p.turnaround_time}")
        total_wait += p.waiting_time
        total_turnaround += p.turnaround_time

    print(f"\nTempo médio de espera: {total_wait / num_processos:.2f}")
    print(f"Tempo médio de retorno: {total_turnaround / num_processos:.2f}")

if __name__ == "__main__":
    # Exemplo: quantum=4, 5 processos
    quantum = int(input("Digite o valor do quantum: "))
    num_processos = int(input("Digite o número de processos: "))
    main(quantum, num_processos)
