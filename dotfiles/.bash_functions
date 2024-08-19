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
