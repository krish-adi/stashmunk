#!/bin/bash

# # TODO: Run pgbouncer as a non-root user
# # Run pgbouncer with its configuration
# pgbouncer /etc/pgbouncer/pgbouncer.ini &

# Start PostgreSQL with the required options
postgres -c "shared_preload_libraries=vector,age"
