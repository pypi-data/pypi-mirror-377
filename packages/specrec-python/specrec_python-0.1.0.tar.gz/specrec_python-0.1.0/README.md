# SpecRec ObjectFactory for Python

A clean, powerful dependency injection factory for making legacy Python code testable with minimal changes.

## Features

- **Minimal Code Changes**: Replace `new` instantiation with factory calls
- **Test Double Injection**: Seamless mocking, stubbing, and spying capabilities
- **Curried Syntax**: Clean functional API inspired by TypeScript implementation
- **Duck Typing**: No complex interface mappings - Python's duck typing handles compatibility
- **Context Managers**: Built-in test isolation with Python's `with` statements
- **Thread Safe**: Concurrent-safe global singleton and test double management
- **Type Hints**: Full type safety for modern Python development
- **All 9 Microfeatures**: Complete implementation of SpecRec ObjectFactory pattern

## Quick Start

### Installation

```bash
pip install specrec-python
```

### Basic Usage

```python
from specrec import create

# Replace this:
service = EmailService("smtp.gmail.com", 587)

# With this:
service = create(EmailService)("smtp.gmail.com", 587)
```

### Test Double Injection

```python
from specrec import create, set_one, context

def test_email_service():
    mock_service = MockEmailService()

    with context():
        set_one(EmailService, mock_service)

        # Your code under test
        user_service = create(UserService)()
        user_service.send_welcome_email("user@example.com")

        # Verify the mock was used
        assert len(mock_service.sent_emails) == 1
```

## API Reference

### Core Functions

#### `create(cls)`

Returns a curried function for creating instances of the specified class.

```python
from specrec import create

# Create a factory function
create_service = create(EmailService)

# Use it multiple times
service1 = create_service("smtp1.example.com", 587)
service2 = create_service("smtp2.example.com", 465)
```

#### `create_direct(cls, *args, **kwargs)`

Create an instance directly with constructor arguments.

```python
from specrec import create_direct

service = create_direct(EmailService, "smtp.gmail.com", port=587, username="user")
```

### Test Double Management

#### Single-Use Test Doubles

```python
from specrec import set_one

def test_service():
    mock = MockEmailService()
    set_one(EmailService, mock)

    # Next creation returns mock
    service = create(EmailService)("smtp.example.com")
    assert service is mock

    # Subsequent creation returns real instance
    service2 = create(EmailService)("smtp.example.com")
    assert isinstance(service2, EmailService)
```

#### Persistent Test Doubles

```python
from specrec import set_always, clear_one

def test_service_always():
    mock = MockEmailService()
    set_always(EmailService, mock)

    # All creations return mock
    service1 = create(EmailService)("smtp.example.com")
    service2 = create(EmailService)("smtp.example.com")
    assert service1 is mock
    assert service2 is mock

    # Clean up
    clear_one(EmailService)
```

### Context Managers for Test Isolation

Python's context managers provide perfect test isolation:

```python
from specrec import context, set_one, create

def test_isolated_mock():
    mock = MockEmailService()

    with context():
        set_one(EmailService, mock)
        service = create(EmailService)("smtp.example.com")
        assert service is mock

    # Outside context, creates real instances
    service2 = create(EmailService)("smtp.example.com")
    assert isinstance(service2, EmailService)
```

### Constructor Parameter Tracking

Track how objects are constructed for debugging and verification:

```python
from specrec.interfaces import IConstructorCalledWith, ConstructorParameterInfo
from typing import List

class TrackedService(IConstructorCalledWith):
    def __init__(self, name: str, port: int, enabled: bool = True):
        self.name = name
        self.port = port
        self.enabled = enabled
        self.constructor_params: List[ConstructorParameterInfo] = []

    def constructor_called_with(self, params: List[ConstructorParameterInfo]) -> None:
        self.constructor_params = params

# Usage
service = create(TrackedService)("api-service", 8080, enabled=False)

print(service.constructor_params)
# [
#     {"index": 0, "name": "name", "value": "api-service", "type_name": "str"},
#     {"index": 1, "name": "port", "value": 8080, "type_name": "int"},
#     {"index": 2, "name": "enabled", "value": False, "type_name": "bool"}
# ]
```

### Object Registration

Register objects with IDs for clean logging and tracking:

```python
from specrec import register_object, get_registered_object

service = create(EmailService)("smtp.gmail.com")
object_id = register_object(service, "main-email-service")

# Later retrieve it
retrieved = get_registered_object("main-email-service")
assert retrieved is service
```

## Migrating Legacy Code

### Before: Direct Instantiation

```python
class UserService:
    def __init__(self):
        self.email_service = EmailService("smtp.company.com", 587)
        self.db = SqlRepository("server=prod;...")

    def create_user(self, email: str) -> User:
        user = User(email)
        self.db.save(user)
        self.email_service.send_welcome(email)
        return user
```

### After: Factory Pattern

```python
from specrec import create

class UserService:
    def __init__(self):
        self.email_service = create(EmailService)("smtp.company.com", 587)
        self.db = create(SqlRepository)("server=prod;...")

    def create_user(self, email: str) -> User:
        user = User(email)
        self.db.save(user)
        self.email_service.send_welcome(email)
        return user
```

### Testable with Minimal Changes

```python
def test_user_service():
    mock_email = MockEmailService()
    mock_db = MockRepository()

    with context():
        set_one(EmailService, mock_email)
        set_one(SqlRepository, mock_db)

        service = UserService()
        user = service.create_user("test@example.com")

        assert len(mock_db.saved_users) == 1
        assert len(mock_email.sent_emails) == 1
```

## Duck Typing Benefits

Python's duck typing eliminates the need for explicit interface mappings:

```python
# No need for explicit interface declarations
class IEmailService:
    def send(self, to: str, subject: str) -> bool: ...

class EmailService:  # No need to explicitly implement IEmailService
    def send(self, to: str, subject: str) -> bool:
        # Real implementation
        return True

class MockEmailService:  # No need to explicitly implement IEmailService
    def send(self, to: str, subject: str) -> bool:
        # Mock implementation
        return True

# Both work seamlessly
service: IEmailService = create(EmailService)("smtp.server")
mock: IEmailService = MockEmailService()
```

## Advanced Usage

### Custom Factory Instances

For advanced scenarios, create dedicated factory instances:

```python
from specrec import ObjectFactory

# Create dedicated factory for a module
api_factory = ObjectFactory()

# Use it independently
create_api_service = api_factory.create(ApiService)
service = create_api_service("https://api.example.com")
```

### Nested Context Managers

```python
def test_nested_contexts():
    outer_mock = MockEmailService()
    inner_mock = MockEmailService()

    with context():
        set_always(EmailService, outer_mock)

        with context():
            set_always(EmailService, inner_mock)
            service = create(EmailService)("smtp.example.com")
            assert service is inner_mock

        # Back to outer context
        service = create(EmailService)("smtp.example.com")
        assert service is outer_mock

    # Outside all contexts
    service = create(EmailService)("smtp.example.com")
    assert isinstance(service, EmailService)
```

## Comparison with Other Languages

| Feature | Python | TypeScript | C# | Java |
|---------|--------|------------|-----|------|
| **API Style** | `create(Class)(args)` | `create(Class)(args)` | `Create<T>(args)` | `create(Class.class).with(args)` |
| **Type Safety** | Type hints | Compile-time | Generics | Generics |
| **Interface Mapping** | Duck typing (not needed) | Duck typing (not needed) | Explicit mapping | Explicit mapping |
| **Test Isolation** | Context managers | Manual cleanup | Manual cleanup | Manual cleanup |
| **Parameter Handling** | `*args, **kwargs` | Type inference | Reflection | Reflection |

## Why Python's Implementation is Special

1. **Duck Typing**: No complex interface-to-implementation mapping
2. **Context Managers**: Built-in test isolation pattern
3. **Flexible Parameters**: `*args, **kwargs` handle any constructor signature
4. **Introspection**: Rich parameter tracking without reflection complexity
5. **Pythonic**: Snake case naming, protocols, and idiomatic patterns

## Contributing

See the main [SpecRec repository](https://github.com/anthropics/specrec) for contribution guidelines.

## License

This project is licensed under the PolyForm Noncommercial License 1.0.0. See LICENSE.md for details.