# dotfiles

Feel at home and work fast no matter which host you're working on. 

## Conda

Remember you can set up Conda via something like the following [Bash snippet available as a Gist](https://gist.github.com/anilkeshwani/60567eaa5fb8c36398c52022afbde22e?permalink_comment_id=4506327#gistcomment-4506327) when on Linux:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh &&
    bash miniconda.sh -b -u -p "${HOME}/miniconda3" &&
    ~/miniconda3/bin/conda init bash &&
    export PATH="${HOME}/miniconda3/bin:${PATH}" &&
    rm -rf miniconda.sh
```

Remember that you want to also create a `main` environment to keep the `base` Conda environment clean:

```bash
conda create --name main --clone base --copy
```

## SSH Keys

When spinning up a new machine, you need to set up SSH keys to authenticate with GitHub

1. Create a new SSH public-private key pair:
  
  ```bash 
  ssh-keygen -t ed25519 -C "anilkeshwani@hotmail.com" &&
      cat "${HOME}/.ssh/id_ed25519.pub"
  ```
  
2. [Add the public key as a new SSH key on GitHub](https://github.com/settings/keys)
