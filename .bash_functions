ngclog() {
    local ngc_log_dir
    ngc_log_dir="${HOME}/ngc-logs"
    if [ ! -d "$ngc_log_dir" ]; then
        echo "${ngc_log_dir} does not exist"
    else
        local ngc_job_logfile
        ngc_job_logfile="${ngc_log_dir}/$1.txt"
        ngc batch log "$1" > "$ngc_job_logfile"
        echo "$ngc_job_logfile"
    fi
}

