import hashlib
import time


class Message:
    def __init__(self, sender_connector, message_type, data):
        self.sender_connector = sender_connector
        self.message_type = message_type
        self.data = data
        self.timestamp = time.time()
        # Create message hash for deduplication
        self.message_id = self._generate_message_id()
    
    def _generate_message_id(self):
        """Generate unique message ID for deduplication"""
        content = f"{self.sender_connector.ip}:{self.sender_connector.port}:{self.message_type}:{self.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def is_recent(self, max_age_seconds=300):
        """Check if message is recent (within max_age_seconds)"""
        return time.time() - self.timestamp <= max_age_seconds
