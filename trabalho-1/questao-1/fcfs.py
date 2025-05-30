import threading
import time
import random

class Processo(threading.Thread):
    def __init__(self, id, burst_time):
        super().__init__()
        self.id = id
        self.burst_time = burst_time
        self.start_time = None
        self.end_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

    def run(self):
        # Simula o tempo de execução do processo
        print(f"[Início] Processo P{self.id} executando por {self.burst_time}s")
        time.sleep(self.burst_time * 0.1)  # Simulação acelerada
        print(f"[Fim] Processo P{self.id} terminou")

def fcfs(processos):
    tempo_atual = 0

    print("\n--- Iniciando escalonamento FCFS ---\n")

    for processo in processos:
        processo.start_time = tempo_atual
        processo.waiting_time = tempo_atual
        tempo_atual += processo.burst_time
        processo.end_time = tempo_atual
        processo.turnaround_time = processo.end_time

        # Executa a thread (representa o tempo de burst)
        processo.start()
        processo.join()

def main(num_processos):
    # Gera burst times aleatórios entre 5 e 15
    processos = [Processo(id=i+1, burst_time=random.randint(5, 15)) for i in range(num_processos)]

    fcfs(processos)

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
    num_processos = int(input("Digite o número de processos: "))
    main(num_processos)
