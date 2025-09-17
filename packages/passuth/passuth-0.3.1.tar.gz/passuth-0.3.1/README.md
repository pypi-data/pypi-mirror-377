# passuth

Python wrapper module for rust crate [password-auth](https://crates.io/crates/password-auth).

It provides a simple and secure way to hash and verify passwords using the Argon2 algorithm, and includes a Fernet-compatible symmetric encryption helper.

## Note

It's my practical project for using Rust in Python, so it may not be the most efficient or optimized solution. You may use well-maintained libraries like `argon2-cffi` or `bcrypt` for production use.

## Usage

### Python API

```python
from passuth import generate_hash, verify_password

hashed = generate_hash("your_password")
print(hashed)
# $argon2id$v=19$m=19456,t=2,p=1$3IF6RWPqOkLk6ZboZ8rPqg$8eEHegumboozWtxJ6X4Fx1++zkvxiKUMIbP+BqgysIo

# To verify
is_valid = verify_password("your_password", hashed)
print("Password valid:", is_valid)
# Password valid: True
```

Accepted input types:

- generate_hash: str | bytes | bytearray | memoryview
- verify_password: str | bytes | bytearray | memoryview (password), str (hash)

#### Fernet (symmetric encryption)

```python
from passuth import Fernet

# Create with a random key
f = Fernet.new()
token = f.encrypt("my secret data")
data = f.decrypt(token)
print(data)  # b'my secret data'

# Or create from an existing key (base64 urlsafe string)
key = Fernet.generate_key()
f2 = Fernet(key)
```

Notes:

- Compatible with cryptography's Fernet tokens/keys in both directions.
- Instances are picklable and support copy/deepcopy.
- Errors (e.g., invalid key/token) raise ValueError.

### Command Line Interface

You can also use `passuth` from the command line:

Hash a password:

```sh
passuth generate your_password
# $argon2id$v=19$m=19456,t=2,p=1$g/wfcEvVbgfhR1ElhZZQ8Q$T0Ax8wFtAFXoRp87SKD7o9zBl3VwQU3/YX6ScRkY6Ts
```

Verify a password:

```sh
passuth verify your_password '$argon2id$v=19$m=19456,t=2,p=1$g/wfcEvVbgfhR1ElhZZQ8Q$T0Ax8wFtAFXoRp87SKD7o9zBl3VwQU3/YX6ScRkY6Ts'
# true
passuth verify wrong_password '$argon2id$v=19$m=19456,t=2,p=1$g/wfcEvVbgfhR1ElhZZQ8Q$T0Ax8wFtAFXoRp87SKD7o9zBl3VwQU3/YX6ScRkY6Ts'
# false
```

Replace `your_password` with your actual password and hash.

## Changelog

### v0.3.0

- New: Fernet symmetric encryption API (`passuth.Fernet`) with `generate_key()`, `new()`, `encrypt()`, `decrypt()`.
- New: Type hints and typings shipped (`passuth.pyi`, `py.typed`).
- Improved: Password inputs now accept bytes-like objects (`bytes`, `bytearray`, `memoryview`) in addition to `str`.
- Improved: Releases the GIL during heavy operations for better concurrency.
- Packaging: Prebuilt wheels include PyPy and CPython free-threading builds where available.

Migration: No breaking API changes from v0.2.0. Existing `generate_hash`/`verify_password` code continues to work. Use the new `Fernet` class for optional encryption needs.

### v0.2.0

- Password hashing (`generate_hash`) using Argon2id and verification (`verify_password`).
- Basic command-line interface: `passuth generate`, `passuth verify`.
