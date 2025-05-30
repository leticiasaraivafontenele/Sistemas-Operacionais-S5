import threading
import time
import random
import matplotlib.pyplot as plt

room_lock = threading.Condition()
dogs_in_room = 0
cats_in_room = 0

dog_states = {}
cat_states = {}

# Lista para armazenar logs (timestamp, dogs, cats)
event_log = []

def log_event():
    timestamp = time.time()
    event_log.append((timestamp, dogs_in_room, cats_in_room))

def dogWantsToEnter(dog_id):
    global dogs_in_room, cats_in_room
    with room_lock:
        if dog_states[dog_id]:
            return
        while cats_in_room > 0:
            print(f"🐶 Dog {dog_id} tentou entrar, mas há gatos.")
            room_lock.wait()
        dogs_in_room += 1
        dog_states[dog_id] = True
        print(f"🐶 Dog {dog_id} entrou (total: {dogs_in_room})")
        log_event()

def catWantsToEnter(cat_id):
    global dogs_in_room, cats_in_room
    with room_lock:
        if cat_states[cat_id]:
            return
        while dogs_in_room > 0:
            print(f"🐱 Cat {cat_id} tentou entrar, mas há cachorros.")
            room_lock.wait()
        cats_in_room += 1
        cat_states[cat_id] = True
        print(f"🐱 Cat {cat_id} entrou (total: {cats_in_room})")
        log_event()

def dogLeaves(dog_id):
    global dogs_in_room
    with room_lock:
        if not dog_states[dog_id]:
            return
        dogs_in_room -= 1
        dog_states[dog_id] = False
        print(f"🐶 Dog {dog_id} saiu (restantes: {dogs_in_room})")
        log_event()
        if dogs_in_room == 0:
            room_lock.notify_all()

def catLeaves(cat_id):
    global cats_in_room
    with room_lock:
        if not cat_states[cat_id]:
            return
        cats_in_room -= 1
        cat_states[cat_id] = False
        print(f"🐱 Cat {cat_id} saiu (restantes: {cats_in_room})")
        log_event()
        if cats_in_room == 0:
            room_lock.notify_all()

def dog_behavior(dog_id):
    while True:
        time.sleep(random.uniform(0.5, 2))
        if random.choice(['enter', 'leave']) == 'enter':
            dogWantsToEnter(dog_id)
        else:
            dogLeaves(dog_id)

def cat_behavior(cat_id):
    while True:
        time.sleep(random.uniform(0.5, 2))
        if random.choice(['enter', 'leave']) == 'enter':
            catWantsToEnter(cat_id)
        else:
            catLeaves(cat_id)

def iniciar_simulacao(n=3):
    for i in range(n):
        dog_states[i] = False
        cat_states[i] = False
        threading.Thread(target=dog_behavior, args=(i,), daemon=True).start()
        threading.Thread(target=cat_behavior, args=(i,), daemon=True).start()

def gerar_grafico():
    times = [e[0] - event_log[0][0] for e in event_log]
    dogs = [e[1] for e in event_log]
    cats = [e[2] for e in event_log]

    plt.plot(times, dogs, label='Cães na sala', color='blue')
    plt.plot(times, cats, label='Gatos na sala', color='orange')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Quantidade na sala')
    plt.title('Movimentação de Cães e Gatos na Sala')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    iniciar_simulacao(3)
    try:
        time.sleep(30)  # Executa a simulação por 30 segundos
    except KeyboardInterrupt:
        pass
    gerar_grafico()
