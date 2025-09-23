#!/bin/bash

# CDF Environment Switcher Function
# Add this to your .zshrc or .bashrc:
# source /path/to/cdfenv.sh

ENVS_DIR="$HOME/envs"
export ENVS_DIR

# Create envs directory if it doesn't exist
if [ ! -d "$ENVS_DIR" ]; then
    mkdir -p "$ENVS_DIR"
fi

# Check if script is being run directly instead of sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "❌ This script must be sourced, not executed directly!"
    echo ""
    echo "Usage:"
    echo "  source ./cdfenv.sh"
    echo "  cdfenv --help"
    echo ""
    echo "Or add this to your ~/.zshrc or ~/.bashrc:"
    echo "  source $(pwd)/cdfenv.sh"
    exit 1
fi

cdfenv() {
    # Handle quiet mode flag
    local quiet_mode=false
    if [[ "$1" == "--quiet" ]]; then
        quiet_mode=true
        shift
    fi
    
    case "$1" in
        --list|-l)
            if [ "$quiet_mode" = false ]; then
            echo "🌍 Available CDF Environments:"
            echo "----------------------------------------"
            fi
            local count=1
            for env_file in "$ENVS_DIR"/.env.*; do
                if [ -f "$env_file" ]; then
                    local filename=$(basename "$env_file")
                    local project=$(echo "$filename" | rev | cut -d. -f1 | rev)
                    if [ "$quiet_mode" = true ]; then
                        echo "$project"
                    else
                    printf " %d. %-20s (%s)\n" "$count" "$project" "$filename"
                    fi
                    ((count++))
                fi
            done
            if [ $count -eq 1 ] && [ "$quiet_mode" = false ]; then
                echo "No environment files found in $ENVS_DIR"
            fi
            ;;
        --current|-c)
            if [ "$quiet_mode" = true ]; then
                echo "${CDF_PROJECT:-}"
            else
            echo "🔍 Current CDF Environment:"
            echo "------------------------------"
            echo "Project:   ${CDF_PROJECT:-Not set}"
            echo "Cluster:   ${CDF_CLUSTER:-Not set}"
            echo "Client ID: ${IDP_CLIENT_ID:0:8}${IDP_CLIENT_ID:+...}"
            fi
            ;;
        --test|-t)
            if [ "$quiet_mode" = false ]; then
                echo "🔍 Testing CDF Environment Connection:"
                echo "-------------------------------------"
            fi
            
            # Check required variables
            local missing_vars=()
            [[ -z "$CDF_PROJECT" ]] && missing_vars+=("CDF_PROJECT")
            [[ -z "$CDF_CLUSTER" ]] && missing_vars+=("CDF_CLUSTER")
            [[ -z "$IDP_CLIENT_ID" ]] && missing_vars+=("IDP_CLIENT_ID")
            [[ -z "$IDP_CLIENT_SECRET" ]] && missing_vars+=("IDP_CLIENT_SECRET")
            [[ -z "$IDP_TOKEN_URL" ]] && missing_vars+=("IDP_TOKEN_URL")
            
            if [ ${#missing_vars[@]} -gt 0 ]; then
                if [ "$quiet_mode" = true ]; then
                    echo "MISSING_VARS"
                    return 1
                else
                    echo "❌ Missing required variables:"
                    for var in "${missing_vars[@]}"; do
                        echo "   - $var"
                    done
                    return 1
                fi
            fi
            
            # Test CDF connection using cdf command if available
            if command -v cdf >/dev/null 2>&1; then
                if [ "$quiet_mode" = false ]; then
                    echo "🔄 Testing connection to CDF..."
                fi
                
                if cdf auth status --quiet >/dev/null 2>&1; then
                    if [ "$quiet_mode" = true ]; then
                        echo "OK"
                    else
                        echo "✅ Connection successful!"
                        echo "🏷️  Project: $CDF_PROJECT"
                        echo "🌐 Cluster: $CDF_CLUSTER"
                    fi
                    return 0
                else
                    if [ "$quiet_mode" = true ]; then
                        echo "AUTH_FAILED"
                    else
                        echo "❌ Authentication failed"
                        echo "💡 Try: cdf auth login"
                    fi
                    return 1
                fi
            else
                if [ "$quiet_mode" = true ]; then
                    echo "NO_CLI"
                else
                    echo "⚠️  CDF CLI not available - cannot test connection"
                    echo "📋 Variables appear to be set correctly"
                fi
                return 0
            fi
            ;;
        --help|-h|"")
            if [ "$1" = "" ]; then
                # Interactive mode
                cdfenv --current
                echo ""
                cdfenv --list
                echo ""
                
                # Get list of env files
                local env_files=()
                for env_file in "$ENVS_DIR"/.env.*; do
                    if [ -f "$env_file" ]; then
                        env_files+=("$env_file")
                    fi
                done
                
                if [ ${#env_files[@]} -eq 0 ]; then
                    echo "No environment files found. Create .env files in $ENVS_DIR"
                    return 1
                fi
                
                echo -n "Select environment (1-${#env_files[@]}), or 'q' to quit: "
                read -r choice
                
                if [ "$choice" = "q" ] || [ "$choice" = "Q" ]; then
                    echo "Cancelled."
                    return 0
                fi
                
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#env_files[@]} ]; then
                    # Handle both bash (0-indexed) and zsh (1-indexed) arrays
                    local selected_file
                    if [ -n "${env_files[0]}" ]; then
                        # bash-style (0-indexed)
                        selected_file="${env_files[$((choice-1))]}"
                    else
                        # zsh-style (1-indexed)
                        selected_file="${env_files[$choice]}"
                    fi
                    
                    # Check for .env file conflicts BEFORE switching
                    if ! check_env_file_conflicts "$quiet_mode"; then
                        return 1
                    fi
                    
                    if [ "$quiet_mode" = false ]; then
                    echo "🔄 Switching to: $(basename "$selected_file")"
                    fi
                    set -a
                    source "$selected_file"
                    set +a
                    
                    # Validate required variables
                    validate_cdf_environment "$quiet_mode"
                    
                    if [ "$quiet_mode" = false ]; then
                    echo "✅ Environment switched successfully!"
                    echo "🏷️  Project: ${CDF_PROJECT:-Not set}"
                    echo "🌐 Cluster: ${CDF_CLUSTER:-Not set}"
                    fi
                else
                    echo "❌ Invalid selection: $choice"
                    return 1
                fi
            else
                echo "CDF Environment Switcher"
                echo ""
                echo "Usage: cdfenv [--quiet] [environment_name|--list|--current|--test|--help]"
                echo ""
                echo "Examples:"
                echo "  cdfenv                   # Interactive mode"
                echo "  cdfenv z-brent          # Switch to environment containing 'z-brent'"
                echo "  cdfenv --list           # List available environments"
                echo "  cdfenv --current        # Show current environment"
                echo "  cdfenv --test           # Test current environment connection"
                echo "  cdfenv --quiet --list   # List environments (script-friendly output)"
                echo "  cdfenv --quiet z-brent  # Switch environment silently"
            fi
            ;;
        *)
            # Switch to specific environment
            local env_name="$1"
            local env_file=""
            
            # Try exact filename match first
            if [ -f "$ENVS_DIR/$env_name" ]; then
                env_file="$ENVS_DIR/$env_name"
            elif [ -f "$ENVS_DIR/.env.$env_name" ]; then
                env_file="$ENVS_DIR/.env.$env_name"
            fi
            
            # If no exact match found yet, try exact match for the pattern .env.cluster.project.env_name
            if [ -z "$env_file" ]; then
                local exact_matches=()
                for file in "$ENVS_DIR"/.env.*."$env_name"; do
                    if [ -f "$file" ]; then
                        local filename=$(basename "$file")
                        local project=$(echo "$filename" | rev | cut -d. -f1 | rev)
                        # Only match if the project name exactly equals env_name
                        if [[ "$project" == "$env_name" ]]; then
                            exact_matches+=("$file")
                        fi
                    fi
                done
                
                if [ ${#exact_matches[@]} -eq 1 ]; then
                    # Get the first element using a different method
                    env_file=$(printf '%s\n' "${exact_matches[@]}" | head -1)
                elif [ ${#exact_matches[@]} -gt 1 ]; then
                    echo "❌ Multiple exact matches found for '$env_name':"
                    for match in "${exact_matches[@]}"; do
                        local filename=$(basename "$match")
                        local project=$(echo "$filename" | rev | cut -d. -f1 | rev)
                        echo "  - $project ($filename)"
                    done
                    echo "Please be more specific."
                    return 1
                fi
            fi
            
            # If still no exact match found, try partial match
            if [ -z "$env_file" ]; then
                # Try partial match - look for the env_name in the filename
                local matches=()
                for file in "$ENVS_DIR"/.env.*; do
                    if [ -f "$file" ]; then
                        local filename=$(basename "$file")
                        # Extract just the project name (last part after final dot)
                        local project=$(echo "$filename" | rev | cut -d. -f1 | rev)
                        if [[ "$filename" == *"$env_name"* ]] || [[ "$project" == *"$env_name"* ]]; then
                            matches+=("$file")
                        fi
                    fi
                done
                
                if [ ${#matches[@]} -eq 1 ]; then
                    # Get the first (and only) match
                    env_file="${matches[0]}"
                elif [ ${#matches[@]} -gt 1 ]; then
                    echo "❌ Multiple matches found for '$env_name':"
                    for match in "${matches[@]}"; do
                        local filename=$(basename "$match")
                        local project=$(echo "$filename" | rev | cut -d. -f1 | rev)
                        echo "  - $project ($filename)"
                    done
                    echo "Please be more specific."
                    return 1
                fi
            fi
            
            if [ -z "$env_file" ]; then
                echo "❌ Environment '$env_name' not found."
                echo ""
                cdfenv --list
                return 1
            fi
            
            # Check for .env file conflicts BEFORE switching
            if ! check_env_file_conflicts "$quiet_mode"; then
                return 1
            fi
            
            local filename=$(basename "$env_file")
            local project=$(echo "$filename" | rev | cut -d. -f1 | rev)
            if [ "$quiet_mode" = false ]; then
            echo "🔄 Switching to: $project ($filename)"
            fi
            set -a
            source "$env_file"
            set +a
            
            # Validate required variables
            validate_cdf_environment "$quiet_mode"
            
            if [ "$quiet_mode" = false ]; then
            echo "✅ Environment switched successfully!"
            echo "🏷️  Project: ${CDF_PROJECT:-Not set}"
            echo "🌐 Cluster: ${CDF_CLUSTER:-Not set}"
            fi
            ;;
    esac
}

# Function to validate CDF environment variables
validate_cdf_environment() {
    local quiet_mode="$1"
    
    # Check required variables
    local missing_vars=()
    [[ -z "$CDF_PROJECT" ]] && missing_vars+=("CDF_PROJECT")
    [[ -z "$CDF_CLUSTER" ]] && missing_vars+=("CDF_CLUSTER")
    [[ -z "$IDP_CLIENT_ID" ]] && missing_vars+=("IDP_CLIENT_ID")
    [[ -z "$IDP_CLIENT_SECRET" ]] && missing_vars+=("IDP_CLIENT_SECRET")
    [[ -z "$IDP_TOKEN_URL" ]] && missing_vars+=("IDP_TOKEN_URL")
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        if [ "$quiet_mode" = false ]; then
            echo ""
            echo "⚠️  Warning: Missing required CDF variables in environment file:"
            for var in "${missing_vars[@]}"; do
                echo "   - $var"
            done
            echo "💡 Please check your environment file configuration"
        fi
        return 1
    fi
    
    return 0
}

# Function to check for and handle .env file conflicts
check_env_file_conflicts() {
    local quiet_mode="$1"
    local current_dir="$(pwd)"
    local env_files=()
    
    # Check for various .env file patterns that toolkit might load
    for pattern in ".env" ".env.*"; do
        if compgen -G "$pattern" > /dev/null 2>&1; then
            for file in $pattern; do
                if [[ -f "$file" || -L "$file" ]]; then
                    env_files+=("$file")
                fi
            done
        fi
    done
    
    if [ ${#env_files[@]} -gt 0 ]; then
        if [ "$quiet_mode" = true ]; then
            # In quiet mode, automatically ignore conflicts
            return 0
        fi
        
        echo ""
        echo "⚠️  WARNING: Found .env file(s) in current directory:"
        echo "   Directory: $current_dir"
        echo ""
        
        for file in "${env_files[@]}"; do
            if [[ -L "$file" ]]; then
                local target=$(readlink "$file")
                echo "   🔗 $file -> $target (symlink)"
            else
                echo "   📄 $file (regular file)"
            fi
        done
        
        echo ""
        echo "🔧 ISSUE: Cognite Toolkit automatically loads .env files from the current directory."
        echo "   This can interfere with environment switching using cdfenv."
        echo ""
        echo "💡 RECOMMENDATION:"
        echo "   • Keep .env files in ~/envs/ directory (managed by cdfenv)"
        echo "   • Remove .env files from project directories"
        echo "   • Use 'cdfenv <environment>' for switching environments"
        echo ""
        
        # Ask user for action
        local action=""
        while [[ "$action" != "r" && "$action" != "i" && "$action" != "s" ]]; do
            echo -n "Choose action: (r)ename/backup files, (i)gnore warning, (s)kip environment switch: "
            read -r action
            action=$(echo "$action" | tr '[:upper:]' '[:lower:]')
        done
        
        case "$action" in
            "r")
                backup_env_files "${env_files[@]}"
                return 0
                ;;
            "i")
                echo "⚠️  Continuing with .env files present - toolkit behavior may be unpredictable"
                return 0
                ;;
            "s")
                echo "🚫 Environment switch cancelled"
                return 1
                ;;
        esac
    fi
    
    return 0
}

# Function to backup/rename conflicting .env files
backup_env_files() {
    local files=("$@")
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    echo ""
    echo "🔄 Backing up .env files..."
    
    for file in "${files[@]}"; do
        local backup_name
        if [[ -L "$file" ]]; then
            # Handle symlinks
            backup_name="${file}.symlink_backup_${timestamp}"
            echo "   🔗 Moving symlink: $file -> $backup_name"
            mv "$file" "$backup_name"
        else
            # Handle regular files
            backup_name="${file}.backup_${timestamp}"
            echo "   📄 Moving file: $file -> $backup_name"
            mv "$file" "$backup_name"
        fi
    done
    
    echo "✅ Files backed up successfully!"
    echo "   To restore: rename files back to original names"
    echo ""
} 