import hashlib
import time

class BlockchainLedger:
    def __init__(self):
        self.chain = []

    def _hash(self, block):
        return hashlib.sha256(str(block).encode()).hexdigest()

    def add_record(self, event_id, buyer_name, tickets_bought):
        block = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_id": event_id,
            "buyer": buyer_name,
            "tickets_bought": tickets_bought,
            "prev_hash": self._hash(self.chain[-1]) if self.chain else "GENESIS",
        }
        block["hash"] = self._hash(block)
        self.chain.append(block)

    def all_records(self):
        return self.chain
