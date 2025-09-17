# Coding conventions

1. Always be performant, focus on avoiding overhead.
2. Always run the code using `PYTHONPATH="" uv run --python 3.13.5 pytest -x -s -k {the test name you care about}` or `PYTHONPATH="" uv run --python 3.13.5 pytest -x -s` for all tests.
3. Never write dirty hacks or workarounds, design and architect robust solutions.
4. Favor event-driven code.
5. Do not references traits inside the orchestrator/worker, use hooks and lifecycles to perform trait execution.
6. All mocking is forbidden. Any use of ANY mocking framework is ILLEGAL.
7. Under no circumstances can tasks, results, or log items be lost.
