import threading
import time
import random
import statistics

# Constantes de simulação
CONTEXT_SWITCH = 1
PROCESS_COUNT = 5
QUANTUMS = [2, 4]  # diferentes quantums para RR

class Processo(threading.Thread):
    def __init__(self, pid, arrival_time, burst_time):
        super().__init__()
        self.id = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.end_time = None
        self.executando = threading.Event()
        self.finalizado = threading.Event()

    def run(self):
        while self.remaining_time > 0:
            self.executando.wait()
            self.executando.clear()
            print(f"[{self.id}] executando (restante={self.remaining_time})")
            time.sleep(1)
            self.remaining_time -= 1
            if self.remaining_time == 0:
                self.finalizado.set()
                print(f"[{self.id}] finalizado")

def gerar_processos(n):
    return [Processo(f'P{i}', random.randint(0, 5), random.randint(2, 6)) for i in range(n)]

def calcular_metricas(processos):
    tempos_espera = [p.start_time - p.arrival_time for p in processos]
    tempos_retorno = [p.end_time - p.arrival_time for p in processos]
    fim_total = max(p.end_time for p in processos)
    throughput = len(processos) / (fim_total + 1)

    return {
        'tempo_medio_espera': (round(statistics.mean(tempos_espera), 2), round(statistics.stdev(tempos_espera), 2) if len(tempos_espera) > 1 else 0),
        'tempo_medio_retorno': (round(statistics.mean(tempos_retorno), 2), round(statistics.stdev(tempos_retorno), 2) if len(tempos_retorno) > 1 else 0),
        'throughput': round(throughput, 2)
    }

def escalonador_nao_preemptivo(processos, criterio='fcfs'):
    tempo = 0
    fila = processos[:]
    prontos = []
    log = []

    for p in processos:
        p.start()

    while fila or prontos:
        prontos += [p for p in fila if p.arrival_time <= tempo]
        fila = [p for p in fila if p not in prontos]

        if not prontos:
            tempo += 1
            time.sleep(1)
            continue

        if criterio == 'sjf':
            prontos.sort(key=lambda p: p.burst_time)
        else:  # fcfs
            prontos.sort(key=lambda p: p.arrival_time)

        p = prontos.pop(0)
        if p.start_time is None:
            p.start_time = tempo

        print(f"\nTempo {tempo}: {p.id} começa execução por {p.burst_time} unidade(s)")
        for _ in range(p.burst_time):
            p.executando.set()
            time.sleep(1)
            tempo += 1

        tempo += CONTEXT_SWITCH
        p.end_time = tempo - CONTEXT_SWITCH
        log.append(p.id)

    for p in processos:
        p.join()

    return processos, log

def round_robin_threaded(processos, quantum):
    tempo = 0
    fila = []
    fila_espera = sorted(processos, key=lambda p: p.arrival_time)
    log = []

    for p in processos:
        p.start()

    while fila or fila_espera:
        while fila_espera and fila_espera[0].arrival_time <= tempo:
            fila.append(fila_espera.pop(0))

        if not fila:
            tempo += 1
            time.sleep(1)
            continue

        proc = fila.pop(0)
        if proc.start_time is None:
            proc.start_time = tempo

        tempo_exec = min(quantum, proc.remaining_time)
        print(f"\nTempo {tempo}: {proc.id} executa RR por {tempo_exec} unidade(s)")
        for _ in range(tempo_exec):
            proc.executando.set()
            time.sleep(1)
            tempo += 1
            if proc.remaining_time <= 0:
                break

        tempo += CONTEXT_SWITCH
        log.append(proc.id)

        if proc.remaining_time > 0:
            while fila_espera and fila_espera[0].arrival_time <= tempo:
                fila.append(fila_espera.pop(0))
            fila.append(proc)
        else:
            proc.end_time = tempo - CONTEXT_SWITCH

    for p in processos:
        p.join()

    return processos, log

def clonar_processos(originais):
    return [Processo(p.id, p.arrival_time, p.burst_time) for p in originais]

def simular_tudo():
    processos_base = gerar_processos(PROCESS_COUNT)

    print("\n--- Processos Criados ---")
    for p in processos_base:
        print(f"{p.id} | chegada: {p.arrival_time} | burst: {p.burst_time}")

    print("\n=== FCFS ===")
    proc_fcfs = clonar_processos(processos_base)
    resultados_fcfs, log_fcfs = escalonador_nao_preemptivo(proc_fcfs, 'fcfs')
    print(f"Ordem de execução: {log_fcfs}")
    print(f"Métricas: {calcular_metricas(resultados_fcfs)}")

    print("\n=== SJF (não-preemptivo) ===")
    proc_sjf = clonar_processos(processos_base)
    resultados_sjf, log_sjf = escalonador_nao_preemptivo(proc_sjf, 'sjf')
    print(f"Ordem de execução: {log_sjf}")
    print(f"Métricas: {calcular_metricas(resultados_sjf)}")

    for q in QUANTUMS:
        print(f"\n=== Round Robin (quantum = {q}) ===")
        proc_rr = clonar_processos(processos_base)
        resultados_rr, log_rr = round_robin_threaded(proc_rr, q)
        print(f"Ordem de execução: {log_rr}")
        print(f"Métricas: {calcular_metricas(resultados_rr)}")

if __name__ == "__main__":
    simular_tudo()