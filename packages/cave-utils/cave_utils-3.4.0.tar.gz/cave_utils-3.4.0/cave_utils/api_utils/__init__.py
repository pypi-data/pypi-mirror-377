"""
## Validation

This code can be used directly for validation purposes:

```py
from cave_utils import Validator

session_data = {
    "kwargs": {
        "wipeExisting": True,
    },
    # All of your session data to validate here
}

x = Validator(
    session_data=session_data,
)

print(x.log.log)
```
"""
