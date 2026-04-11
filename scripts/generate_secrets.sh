#!/usr/bin/env bash

set -euo pipefail

# Generates a random hex string of specified length
#
# Parameters:
# - $1: int - length of the hex string to generate (default: 32)
#
# Returns:
# - string: random hex string
generate_hex() {
    local length=${1:-32}
    openssl rand -hex "$length"
}

# Generates Redis password
#
# Parameters:
# - None
#
# Returns:
# - string: generated Redis password
generate_redis_password() {
    generate_hex 32
}

# Generates SearxNG secret key
#
# Parameters:
# - None
#
# Returns:
# - string: generated SearxNG secret key
generate_searxng_secret_key() {
    generate_hex 32
}

# Generates PostgreSQL password
#
# Parameters:
# - None
#
# Returns:
# - string: generated PostgreSQL password
generate_postgres_password() {
    generate_hex 32
}

# Generates BULL auth key
#
# Parameters:
# - None
#
# Returns:
# - string: generated BULL auth key
generate_bull_auth_key() {
    generate_hex 32
}

# Main orchestration entrypoint
#
# Parameters:
# - $@: array - command-line invocation arguments
#
# Returns:
# - None (prints secrets to stdout)
main() {
    case "$1" in
        redis_password)
            generate_redis_password
            ;;
        searxng_secret_key)
            generate_searxng_secret_key
            ;;
        postgres_password)
            generate_postgres_password
            ;;
        bull_auth_key)
            generate_bull_auth_key
            ;;
        all)
            echo "REDIS_PASSWORD=$(generate_redis_password)"
            echo "SEARXNG_SECRET_KEY=$(generate_searxng_secret_key)"
            echo "POSTGRES_PASSWORD=$(generate_postgres_password)"
            echo "BULL_AUTH_KEY=$(generate_bull_auth_key)"
            ;;
        *)
            echo "Usage: $0 [redis_password|searxng_secret_key|postgres_password|bull_auth_key|all]"
            exit 1
            ;;
    esac
}

main "$@"