ngclog() {
    local ngc_log_dir
    ngc_log_dir="${HOME}/ngc-logs"
    if [ ! -d "$ngc_log_dir" ]; then
        echo "${ngc_log_dir} does not exist"
    else
        local ngc_job_logfile
        ngc_job_logfile="${ngc_log_dir}/$1.txt"
        ngc batch log "$1" >"$ngc_job_logfile"
        echo "$ngc_job_logfile"
    fi
}

sshkeyadd() {
    local ssh_key_path
    ssh_key_path="${HOME}/.ssh/id_ed25519"
    eval "$(ssh-agent -s)"
    ssh-add "$ssh_key_path"
}

file_ends_with_newline() {
    [[ $(tail -c1 "$1" | wc -l) -gt 0 ]]
}

git_first_commit_date() {
    if [ $# -eq 0 ]; then
        echo "Usage: git_first_commit <file_path>"
        return 1
    fi

    local file_path="$1"
    if [ ! -f "$file_path" ]; then
        echo "Error: File not found: $file_path"
        return 1
    fi

    local first_commit=$(git log --reverse --date=format:"%a %b %d %T %Y %z" --pretty=format:"%ad" -- "$file_path" 2>/dev/null | head -1)
    local iso_date=$(git log --reverse --date=iso8601-strict --pretty=format:"%ad" -- "$file_path" 2>/dev/null | head -1)

    if [ -z "$first_commit" ]; then
        echo "Error: No commit history found for $file_path"
        return 1
    fi

    echo "First commit date for ${file_path}: ${first_commit} (${iso_date})"
}

set-gpu() {
    if [ -z "$1" ]; then
        echo "Enter the GPU ID(s) comma-separated for multiple GPUs, e.g., 0,1:"
        read -r gpu_ids
    else
        gpu_ids="$1"
    fi
    export CUDA_VISIBLE_DEVICES=$gpu_ids
    echo "CUDA_VISIBLE_DEVICES set to: $CUDA_VISIBLE_DEVICES"
}
