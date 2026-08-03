# Start Procedure

1. Open the deployed media directory.

   ```bash
   cd /srv/media
   ```

2. Set the Compose command for the environment.

   Production:

   ```bash
   COMPOSE=(sudo docker compose \
     --env-file .env.prod \
     -f compose.yaml \
     -f compose.prod.yaml)
   ```

   Staging:

   ```bash
   COMPOSE=(sudo docker compose \
     --env-file .env.staging \
     -f compose.yaml \
     -f compose.staging.yaml)
   ```

3. Validate the Compose configuration.

   ```bash
   "${COMPOSE[@]}" config --quiet
   ```

4. Start the stack.

   ```bash
   "${COMPOSE[@]}" up -d
   ```

5. Display the complete stack state.

   ```bash
   "${COMPOSE[@]}" ps -a
   ```

6. Display startup logs.

   ```bash
   "${COMPOSE[@]}" logs --tail=100
   ```
