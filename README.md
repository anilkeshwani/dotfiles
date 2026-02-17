# dotfiles

Feel at home and work fast no matter which host you're working on. 

## Dotfiles Management (chezmoi)

This repo now uses [`chezmoi`](https://www.chezmoi.io/) as the primary dotfiles manager while keeping the same Git history and remote.

- Canonical `chezmoi` source-state files live in `home/` (for example `home/dot_zshrc`, `home/dot_gitconfig`, and `home/dot_config/nvim/init.lua`).

### Setup

Install `chezmoi`:

```bash
sh -c "$(curl -fsLS get.chezmoi.io)"
```

From this repo root, preview and apply:

```bash
./install_dotfiles.py --dry-run
./install_dotfiles.py
```

The installer wraps:

```bash
chezmoi init --source "$PWD/home"
chezmoi -S "$PWD/home" apply -v
```

### Day-to-day Usage

Run `chezmoi` directly against this repo as source:

```bash
chezmoi -S "$PWD/home" diff
chezmoi -S "$PWD/home" status
chezmoi -S "$PWD/home" apply -v
```

Update from remote and apply:

```bash
git pull
chezmoi -S "$PWD/home" apply -v
```

### Migration Notes

- `install_dotfiles.py` now uses `chezmoi` by default.
- The previous symlink installer is available temporarily as:

  ```bash
  ./install_dotfiles.py --legacy-fallback
  ```

- Bitwarden integration is planned but not wired yet in templates/scripts.

## Conda

Remember you can set up Conda via something like the following [Bash snippet available as a Gist](https://gist.github.com/anilkeshwani/60567eaa5fb8c36398c52022afbde22e?permalink_comment_id=4506327#gistcomment-4506327) when on Linux:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh &&
    bash miniconda.sh -b -u -p "${HAFH:-${HOME}}/miniconda3" &&
    "${HAFH:-${HOME}}"/miniconda3/bin/conda init bash &&
    export PATH="${HAFH:-${HOME}}/miniconda3/bin:${PATH}" &&
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

## Scripts

Common scripts centralised here for use agnostic of machine. 

### SageMaker Connect (sagemaker_connect.sh)

> [!note]
> Source: [Set up local Visual Studio Code](https://docs.aws.amazon.com/sagemaker/latest/dg/remote-access-local-ide-setup.html), specifically [Method 3: Connect from the terminal via SSH CLI](https://docs.aws.amazon.com/sagemaker/latest/dg/remote-access-local-ide-setup.html#remote-access-local-ide-setup-local-vs-code-method-3-connect-from-the-terminal-via-ssh-cli).

Make the script executable:

```bash
chmod +x /path/to/sagemaker_connect.sh
```

Configure $HOME/.ssh/config to add the following entry:

```bash
Host space-name
  HostName 'arn:PARTITION:sagemaker:us-east-1:111122223333:space/domain-id/space-name'
  ProxyCommand '/path/to/sagemaker_connect.sh' '%h' AWS_PROFILE_NAME
  ForwardAgent yes
  AddKeysToAgent yes
  StrictHostKeyChecking accept-new
```

Breakdown of the `HostName`:
- 'arn:PARTITION:sagemaker:us-east-1:111122223333:space/domain-id/space-name'

For example, the PARTITION can be aws.

If you need to use a [named AWS credential profile](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html#cli-configure-files-using-profiles), change the proxy command as follows:

```bash
ProxyCommand '/path/to/sagemaker_connect.sh' '%h' YOUR_CREDENTIAL_PROFILE_NAME
```

Connect via SSH or run SCP command:

```bash
ssh space-name
scp file_abc space-name:/tmp/
```
