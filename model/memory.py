from memory_slot import MemorySlot
import random

class Memory:
    def __init__(self, capacitym):
        self.capacity = capacity
        self.memory = [MemorySlot]

    def push(self, memory_slot: MemorySlot):
        self.memory.append(memory_slot)
        if len(self.memory) > self.capacity:
            del self.memory[0]

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)