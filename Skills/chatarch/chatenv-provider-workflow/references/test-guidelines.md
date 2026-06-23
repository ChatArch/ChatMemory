# Provider Test Guidelines

Use a local `test()` implementation when the provider's main need is discoverability and schema validation.

Local validation usually means:

- printing the provider title;
- confirming defaults or configured values are readable;
- showing whether optional auth material is present without printing it.

Use a remote `test()` only when:

- the provider already represents a remote service integration;
- the network behavior is part of the documented contract;
- failure modes are understandable to the user.

Avoid remote tests when they would:

- spend money or quota by default;
- mutate server state;
- depend on fragile personal infrastructure;
- leak secrets through logs or error messages.
