"""
This package provides a simple model structure for redis based storage.
It acts like an ORM and allows you to create models with validation.

```python
from redis_mdoels.models import RedisModelMeta

class User(metaclass=RedisModelMeta):
    name: str
    age: int

    class Meta:
        redis_url = "redis://localhost:6379/0"


user = User(name="John Doe", age=30)
user.save()  # This writes the record to redis

print(user.id)  # This gives you the key for that object

user_again = User.get(id=user.id)

print(user.asdict())  # This gives you a dictionary for that object

user_again.delete()  # This deletes the object

user_not_found = User.get(id=user_again.id)  # The id for the object lives, but the object is gone.

# You should see `redis_models.errors.NotFound` exception

```
"""

__version__ = "0.0.4"
