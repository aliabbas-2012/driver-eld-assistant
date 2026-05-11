# Postman

Import **`Driver_ELD_Assistant.postman_collection.json`** into Postman.

- Set **`base_url`** to your API origin (default `http://127.0.0.1:8000`).
- Run **POST Token** under **Auth** first; the collection test script saves **`access`** and **`refresh`** for requests that use Bearer auth.
- After `python manage.py seed_demo`, use username **`demodriver`** and password **`demo12345`** for login.
