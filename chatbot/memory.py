# memory.py
from langchain.schema import AIMessage, HumanMessage
from collections import deque

class ConversationMemory:
    def __init__(self, max_len=10):
        self.max_len = max_len
        self.human_history = deque(maxlen=max_len)
        self.ai_history = deque(maxlen=max_len)

    def add_human_message(self, text):
        self.human_history.append(HumanMessage(content=text))

    def add_ai_message(self, text):
        self.ai_history.append(AIMessage(content=text))

    def get_memory(self):
        """
        Returns a combined list of past conversation messages in order:
        [HumanMessage, AIMessage, ...]
        """
        memory = []
        for h, a in zip(self.human_history, self.ai_history):
            memory.append(h)
            memory.append(a)
        if len(self.human_history) > len(self.ai_history):
            memory.append(self.human_history[-1])
        return memory

    def get_memory_text(self):
        """
        Returns memory as a formatted string for prompt insertion.
        Example:
        Human: Hi
        AI: Hello! How can I help you today?
        """
        formatted = []
        for msg in self.get_memory():
            role = "Human" if isinstance(msg, HumanMessage) else "AI"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)
    
    def clear(self):
        self.human_history.clear()
        self.ai_history.clear()