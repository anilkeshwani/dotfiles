# Improvements, Requirements, Requests

1. Align the settings in the Bash and Zsh configurations (.rc files) and ensure that the same functionality is provided in both
1. Modularise the OS-specific logic in the .bashrc and .zshrc files by leveraging chezmoi correctly and according to recommended and best practices (see the docs at: https://www.chezmoi.io/user-guide/manage-machine-to-machine-differences/#use-templates and more generally https://www.chezmoi.io/)
1. Separate out the machine-specific logic from the .bashrc and .zshrc files
    - e.g. the .bashrc and .zshrc files contain logic for both Artemis, Poseidon and other servers like those rented via Vast - these are all Linux (Ubuntu usually) but require different configurations
1. Eliminate all references to user-specific or sensitive data by leveraging chezmoi and Bitwarden
    - e.g. the README contains my personal email address
1. Retroactively remove such committed data from the repository
    - use something like gitleaks
1. Leverage Bitwarden to load in secrets such as ssh keys, api keys, etc. (see the docs at: https://www.chezmoi.io/reference/templates/bitwarden-functions/)
1. Run gitleaks to identify any other sensitive data that may have been committed to the repository
    - and remove it
