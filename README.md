# Interpreter

## How to Run
```
    python3 src/interpreter.py  (--dynamic | --static) FILE
```
With `--dynamic` and `--static` representing the different types of scopes for variables.

With `FILE` being the path of the source program.

Example:
```
    python3 src/interpreter.py test/test_program_1.ag --static
```

During execution you can press `ENTER` to go to the next statement.
