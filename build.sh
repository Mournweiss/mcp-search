#!/usr/bin/env bash

set -euo pipefail

# ANSI color codes
COLOR_INFO="\033[0m"       # White (default)
COLOR_WARN="\033[1;33m"    # Yellow
COLOR_ERROR="\033[1;31m"   # Red
COLOR_SUCCESS="\033[1;32m" # Green
COLOR_RESET="\033[0m"

info()    { echo -e "${COLOR_INFO}$1${COLOR_RESET}" >&2; }
warn()    { echo -e "${COLOR_WARN}$1${COLOR_RESET}" >&2; }
error()   { echo -e "${COLOR_ERROR}$1${COLOR_RESET}" >&2; exit 1; }
success() { echo -e "${COLOR_SUCCESS}$1${COLOR_RESET}" >&2; }

compose_file="compose.yml"
env_file=".env"
NO_KEYGEN_MODE=false
FOREGROUND_MODE=false

# Parses command-line arguments and sets global variables for orchestrator and options.
#
# Parameters:
# - $@: array - command-line arguments
#
# Returns:
# - None (sets global shell vars)
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --podman|-p)
                ORCHESTRATOR="podman-compose"
                shift
                ;;
            --docker|-d)
                ORCHESTRATOR="docker-compose"
                shift
                ;;
            --foreground|-f)
                FOREGROUND_MODE="true"
                shift
                ;;
            --no-keygen|-n)
                NO_KEYGEN_MODE="true"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                warn "Unknown argument: $1"
                shift
                ;;
        esac
    done
}

# Shows help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --podman|-p                     Use podman-compose instead of docker-compose"
    echo "  --docker|-d                     Use docker-compose instead of podman-compose"
    echo "  --foreground|-f                 Run in foreground mode"
    echo "  --no-keygen|-n                  Skip secret generation"
    echo "  --help|-h                       Show this help message"
    echo ""
}

# Checks if a given orchestrator command is installed and available.
#
# Parameters:
# - $1: string - orchestrator name ("docker-compose", "podman-compose", "docker compose")
#
# Returns:
# - 0: success, 1: not available
is_orchestrator_available() {
    case "$1" in
        docker-compose)
            command -v docker-compose &>/dev/null && return 0 || return 1
            ;;
        "docker compose")
            command -v docker &>/dev/null && docker compose version &>/dev/null && return 0 || return 1
            ;;
        podman-compose)
            command -v podman-compose &>/dev/null && return 0 || return 1
            ;;
        *)
            return 1
            ;;
    esac
}

# Selects and validates best-available container orchestrator, or uses argument if set.
#
# Parameters:
# - None (uses global ORCHESTRATOR)
#
# Returns:
# - string: orchestrator command or exits with error
select_orchestrator() {
    local candidates=("docker-compose" "docker compose" "podman-compose")
    if [ -n "$ORCHESTRATOR" ]; then
        if is_orchestrator_available "$ORCHESTRATOR"; then
            echo "$ORCHESTRATOR"
            return 0
        else
            error "$ORCHESTRATOR not found."
        fi
    else
        for orch in "${candidates[@]}"; do
            if is_orchestrator_available "$orch"; then
                echo "$orch"
                return 0
            fi
        done
        error "No supported container orchestrator found"
    fi
}

# Ensures all variables from the template are present in the actual env file.
#
# Parameters:
# - template_file: string - path to the template .env file (e.g., .env.example)
# - env_file: string - path to the target .env file
#
# Returns:
# - None
ensure_env_vars() {
    local template_file="$1"
    local env_file="$2"
    local updated=0
    info "Syncing .env with template: $template_file"
    
    # Read all variables from template
    local template_vars=$(read_env_file -f "$template_file")
    
    # Process each variable from the template
    for var in $template_vars; do
        [[ -z "$var" ]] && continue
        
        local var_name="${var%%=*}"
        [[ "$var_name" =~ ^[[:space:]]*# ]] && continue
        
        info "Checking if $var_name is present in $env_file ..."
        if ! grep -Eq "^[[:space:]]*#?[[:space:]]*$var_name[[:space:]]*=" "$env_file"; then
            last_char=$(tail -c1 "$env_file" 2>/dev/null || echo '')
            if [[ "$last_char" != "" && "$last_char" != $'\n' ]]; then
                echo >> "$env_file"
            fi
            echo "$var" >> "$env_file"
            info "Added $var_name to $env_file"
            updated=1
        fi
    done
    
    if [[ $updated -eq 1 ]]; then
        info "Completed variable sync: $env_file updated"
    else
        info "No missing variables detected in $env_file"
    fi
}

# Read environment variables from file and return them as a space-separated string
#
# Parameters:
# - $@: array - command-line arguments for specifying file and variables
#   --file|-f <file>: specify the environment file to read (default: .env)
#   --value|-v: return only values, not key=value pairs
#   other args: specific variable names to read (comma-separated)
#
# Returns:
# - string: space-separated environment variables in key=value format or just values if --value flag is used
read_env_file() {
    local env_file=""
    local vars_to_read=()
    local value_only=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --value|-v)
                value_only=true
                shift
                ;;
            --file|-f)
                if [[ -n "$2" && "$2" != "--"* ]]; then
                    env_file="$2"
                    shift 2
                else
                    error "Missing file argument for --file flag"
                fi
                ;;
            --file=*)
                env_file="${1#*=}"
                shift
                ;;
            *)
                if [[ -n "$env_file" ]]; then
                    IFS=',' read -ra vars <<< "$1"
                    for var in "${vars[@]}"; do
                        vars_to_read+=("$var")
                    done
                else
                    env_file="$1"
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$env_file" ]]; then
        env_file=".env"
    fi
    
    if [[ ! -f "$env_file" ]]; then
        info "Environment file $env_file not found"
        return 1
    fi
    
    local env_args=""
    
    # Read and process each line
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Extract variable name and value
        local var_name="${line%%=*}"
        local var_value="${line#*=}"
        
        # Remove trailing comments and trim whitespace
        var_value="${var_value%%#*}"
        var_name="$(echo "$var_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        var_value="$(echo "$var_value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        
        # Skip if variable name is empty
        [[ -z "$var_name" ]] && continue
        
        # If specific variables are requested, check if this one matches
        if [[ ${#vars_to_read[@]} -gt 0 ]]; then
            local found=false
            for var in "${vars_to_read[@]}"; do
                if [[ "$var" == "$var_name" ]]; then
                    found=true
                    break
                fi
            done
            [[ "$found" == false ]] && continue
        fi
        
        # Handle output format based on value_only flag
        if [[ "$value_only" == true ]]; then
            echo "$var_value"
        else
            # Return key=value pairs
            if [[ -n "$env_args" ]]; then
                env_args="$env_args $var_name=$var_value"
            else
                env_args="$var_name=$var_value"
            fi
        fi
    done < "$env_file"
    
    # Output all variables
    if [[ "$value_only" == false ]]; then
        echo "$env_args"
    fi
}

# Verifies or creates .env file from example.
#
# Parameters:
# - None (uses shell globals)
#
# Returns:
# - None
make_env() {
    if [[ -f .env ]]; then
        info "Using existing .env"
        ensure_env_vars .env.example .env
    else
        [[ -f .env.example ]] || error "No key/.env.example template found"
        info "Creating .env from .env.example..."
        local temp_env=""
        temp_env=$(read_env_file -f .env.example)
        echo "$temp_env" | tr ' ' '\n' > .env
        success "Created .env from .env.example"
    fi
}

# Generates secrets and writes them to env file
#
# Parameters:
# - None
#
# Returns:
# - None (writes to env file)
generate_secrets() {
    if [[ -x "./scripts/generate_secrets.sh" ]]; then
        info "Generating required secrets..."
        
        # Generate all secrets and append them to the env file
        local secrets=$("./scripts/generate_secrets.sh" all)
        
        # Write each secret to the env file
        while IFS= read -r line; do
            if [[ -n "$line" ]]; then
                # Check if variable already exists in env file
                if grep -q "^${line%%=*}=" "$env_file"; then
                    # Update existing variable
                    sed -i "s/^${line%%=*}=.*$/$line/" "$env_file"
                else
                    # Add new variable
                    echo "$line" >> "$env_file"
                fi
            fi
        done <<< "$secrets"
        
        success "Secrets generated and written to $env_file"
    else
        error "generate_secrets script not found or not executable"
    fi
}

# Stops all previous containers, then builds and starts project in either foreground or detached mode according to FOREGROUND_MODE.
#
# Parameters:
# - None
#
# Returns:
# - None
run_project() {
    local orchestrator=$(select_orchestrator)
    info "Stopping and cleaning up any running containers..."
    $orchestrator --env-file "$env_file" -f "$compose_file" down -v || warn "Down failed or nothing to remove"
    success "Previous containers removed"
    info "Building and starting project in $([ "$FOREGROUND_MODE" = "true" ] && echo "foreground" || echo "detached") mode..."
    if [ "$FOREGROUND_MODE" = "true" ]; then
        $orchestrator --env-file "$env_file" -f "$compose_file" up --build
    else
        $orchestrator --env-file "$env_file" -f "$compose_file" up --build -d
    fi
    success "App started in $([ "$FOREGROUND_MODE" = "true" ] && echo "foreground" || echo "detached") mode"
}

# Main orchestration entrypoint
#
# Parameters:
# - $@: array - command-line invocation arguments
#
# Returns:
# - None
main() {
    parse_args "$@"
    make_env
    if [ "$NO_KEYGEN_MODE" = "false" ]; then
        generate_secrets
    else
        info "Skipping secrets generation"
    fi
    run_project
}

main "$@"