#!/usr/bin/env bash

set -euo pipefail
shopt -s dotglob

DEFAULT_DOTFILES_DIR="${HOME}/_default_dotfiles"

mk_default_dotfiles_dir() {
    if [ ! -d "${DEFAULT_DOTFILES_DIR}" ]; then
        mkdir "${DEFAULT_DOTFILES_DIR}"
        echo "Created directory to store existing default dotfiles at ${DEFAULT_DOTFILES_DIR}"
    fi
}

(
    cd dotfiles
    # move existing dotfiles in $HOME to DEFAULT_DOTFILES_DIR
    for file in *; do
        if [ -f "${HOME}/${file}" ]; then
            mk_default_dotfiles_dir
            mv "${HOME}/${file}" "${DEFAULT_DOTFILES_DIR}/${file}"
            echo "Moved ${HOME}/${file} to ${DEFAULT_DOTFILES_DIR}/${file}"
        else
            unlink "${HOME}/${file}"
            echo "Did not find ${HOME}/${file}. Performed unlinking on danling symbolic links"
        fi
    done
    # create soft links in $HOME directory for repository dotfiles
    for file in *; do
        ln -s $(realpath ${file}) "${HOME}/${file}"
    done
)
