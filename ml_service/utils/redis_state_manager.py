import redis
import json
import time

class RedisStateManager:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.client.ping() # Check connection
            print("[INFO] Connected to Redis")
        except redis.ConnectionError:
            print("[WARNING] Redis connection failed. State management will be disabled.")
            self.client = None

    def update_object_state(self, object_id, data, ttl=3600):
        """
        Updates the state of an object in Redis.
        data: dictionary containing object attributes
        ttl: time to live in seconds (default 1 hour)
        """
        if not self.client:
            return

        key = f"object:{object_id}"
        # Convert all values to string for Redis compatibility if needed, 
        # but json.dumps for complex structures is better if storing as a single hash or string.
        # Here we use HSET for individual fields for easier updates.
        
        if not data:
            return

        # Flatten dictionary for hset (redis hset doesn't support nested dicts directly unless stringified)
        flat_data = {}
        for k, v in data.items():
            if v is None:
                continue # Skip None values or convert to "None" string? Let's skip to be safe if that's the intent, or str it.
                # Actually, standard behavior in this app seems to be str(v).
                # But if str(v) is "None", it is a valid string.
            
            if isinstance(v, (dict, list)):
                flat_data[k] = json.dumps(v)
            else:
                flat_data[k] = str(v)
        
        if not flat_data:
            return

        try:
            self.client.hset(key, mapping=flat_data)
            self.client.expire(key, ttl)
        except Exception as e:
            print(f"[ERROR] Redis HSET failed for {key}: {e}. Data: {flat_data}")

    def get_object_state(self, object_id):
        """
        Retrieves the state of an object from Redis.
        """
        if not self.client:
            return {}

        key = f"object:{object_id}"
        data = self.client.hgetall(key)
        
        # Unpack JSON fields and convert types
        processed_data = {}
        for k, v in data.items():
            try:
                # Try loading as JSON
                processed_data[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # Keep as string or convert numeric
                if v.replace('.', '', 1).isdigit():
                     processed_data[k] = float(v) if '.' in v else int(v)
                else:
                    processed_data[k] = v
                    
        return processed_data

    def delete_object(self, object_id):
        if self.client:
            self.client.delete(f"object:{object_id}")

    def get_all_active_objects(self):
        if not self.client:
            return []
        keys = self.client.keys("object:*")
        objects = []
        for key in keys:
            obj_id = key.split(":")[1]
            objects.append(self.get_object_state(obj_id))
        return objects
    
    def set_owner_state(self, owner_id, data, ttl=3600):
        if not self.client:
            return
        key = f"owner:{owner_id}"
        flat_data = {k: str(v) for k, v in data.items()}
        self.client.hset(key, mapping=flat_data)
        self.client.expire(key, ttl)
        
    def get_owner_state(self, owner_id):
        if not self.client:
            return {}
        return self.client.hgetall(f"owner:{owner_id}")
