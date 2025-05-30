import threading
import time
import random

class VetHospital:
    def __init__(self):
        self.lock = threading.Lock()
        self.dogs = 0
        self.cats = 0
        self.room_state = "Vazia"
        self.room_condition = threading.Condition(self.lock)

    def dogWantsToEnter(self, dog_id):
        with self.room_condition:
            print(f"Cachorro {dog_id} quer entrar...")
            if self.room_state == "Gatos":
                print(f"Cachorro {dog_id} MISS - sala ocupada por gatos.\n")
            while self.room_state == "Gatos":
                self.room_condition.wait()
            self.dogs += 1
            self.room_state = "Cachorros"
            print(f"Cachorro {dog_id} HIT - entrou. Cachorros na sala: {self.dogs}")

    def dogLeaves(self, dog_id):
        with self.room_condition:
            self.dogs -= 1
            print(f"Cachorro {dog_id} saiu. Cachorros restantes: {self.dogs}")
            if self.dogs == 0:
                self.room_state = "Vazia"
                self.room_condition.notify_all()

    def catWantsToEnter(self, cat_id):
        with self.room_condition:
            print(f"Gato {cat_id} quer entrar...")
            if self.room_state == "Cachorros":
                print(f"Gato {cat_id} MISS - sala ocupada por cachorros.\n")
            while self.room_state == "Cachorros":
                self.room_condition.wait()
            self.cats += 1
            self.room_state = "Gatos"
            print(f"Gato {cat_id} HIT - entrou. Gatos na sala: {self.cats}")

    def catLeaves(self, cat_id):
        with self.room_condition:
            self.cats -= 1
            print(f"Gato {cat_id} saiu. Gatos restantes: {self.cats}")
            if self.cats == 0:
                self.room_state = "Vazia"
                self.room_condition.notify_all()

def dog_behavior(hospital, dog_id):
    hospital.dogWantsToEnter(dog_id)
    time.sleep(random.uniform(0.5, 2))
    hospital.dogLeaves(dog_id)

def cat_behavior(hospital, cat_id):
    hospital.catWantsToEnter(cat_id)
    time.sleep(random.uniform(0.5, 2))
    hospital.catLeaves(cat_id)

hospital = VetHospital()
threads = []

for i in range(5):
    t = threading.Thread(target=dog_behavior, args=(hospital, i))
    threads.append(t)

for i in range(5):
    t = threading.Thread(target=cat_behavior, args=(hospital, i))
    threads.append(t)

random.shuffle(threads)

for t in threads:
    t.start()

for t in threads:
    t.join()