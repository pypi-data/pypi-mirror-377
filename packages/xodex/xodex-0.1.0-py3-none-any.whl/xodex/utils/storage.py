import pickle

class Serializer:
    """
    Base class for serialization logic.

    Subclass and override `serialize()` to provide custom serialization logic.
    """
    def serialize(self) -> dict:
        """
        Serialize the object to a dictionary.

        Returns:
            dict: Serialized representation of the object.
        """
        raise NotImplementedError("serialize() must be implemented by subclasses.")

class Deserializer:
    """
    Base class for deserialization logic.

    Subclass and override `deserialize()` to provide custom deserialization logic.
    """
    def deserialize(self, data: dict) -> None:
        """
        Deserialize the object from a dictionary.

        Args:
            data (dict): Data to restore the object state.
        """
        raise NotImplementedError("deserialize() must be implemented by subclasses.")

class BinarySerializer:
    """
    Base class for binary serialization logic.

    Subclass and override `serialize_binary()` for custom binary serialization.
    By default, uses pickle to serialize the result of `serialize()`.
    """
    def serialize_binary(self) -> bytes:
        """
        Serialize the object to bytes.

        Returns:
            bytes: Serialized binary data.
        """
        return pickle.dumps(self.serialize())

class BinaryDeserializer:
    """
    Base class for binary deserialization logic.

    Subclass and override `deserialize_binary()` for custom binary deserialization.
    By default, uses pickle to load a dict and passes it to `deserialize()`.
    """
    def deserialize_binary(self, data: bytes) -> None:
        """
        Deserialize the object from bytes.

        Args:
            data (bytes): Binary data to restore the object state.
        """
        self.deserialize(pickle.loads(data))

class JsonSerializer:
    """
    Mixin for JSON serialization.

    Recursively serializes attributes that are also JsonSerializer instances.
    """
    def serialize(self) -> dict:
        data = {}
        for key in sorted(self.__dict__):
            key_var = getattr(self, key)
            if isinstance(key_var, JsonSerializer):
                data[key] = key_var.serialize()
                continue
            data[key] = key_var
        return data

class JsonDeserializer:
    """
    Mixin for JSON deserialization.

    Recursively deserializes attributes that are also JsonDeserializer instances.
    """
    def deserialize(self, value: dict) -> None:
        for key in value:
            if not hasattr(self, key):
                continue
            key_var = getattr(self, key)
            if not isinstance(key_var, JsonDeserializer):
                setattr(self, key, value[key])
                continue
            key_var.deserialize(value[key])
            setattr(self, key, key_var)

