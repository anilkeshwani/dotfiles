# dotfiles

Feel at home and work fast no matter which host you're working on. 

## Setup

Dotfiles live in `home/` and are installed as symlinks into `$HOME` via `install_dotfiles.py`. Existing files are backed up to `~/.local/state/dotfiles-backups/` before being replaced.

Preview what would change:

```bash
uv run --script install_dotfiles.py --dry-run
```

Apply:

```bash
uv run --script install_dotfiles.py
```

## SSH Keys

When spinning up a new machine, you need to set up SSH keys to authenticate with GitHub

1. Create a new SSH public-private key pair:
  
  ```bash 
  ssh-keygen -t ed25519 -C "anilkeshwani@hotmail.com" &&
      cat "${HOME}/.ssh/id_ed25519.pub"
  ```
  
2. [Add the public key as a new SSH key on GitHub](https://github.com/settings/keys)

## Bootstrapping New Instances / Machines

### Hints - Bootstrapping

- A good old `exec bash` is always handy
- Vast instances throw you into tmux by default - nice but the tmux config needs reloading once dotfiles are in: **press the old prefix (CtrlB), :`source-file ~/.tmux.conf`**
  - Source: [How do I reload TMUX configuration?](https://superuser.com/questions/580992/how-do-i-reload-tmux-configuration)

Bootstrap and install scripts live in `scripts/`.

### SageMaker Connect (`bootstrap/aws/sagemaker_connect.sh`)

> [!note]
> Source: [Set up local Visual Studio Code](https://docs.aws.amazon.com/sagemaker/latest/dg/remote-access-local-ide-setup.html), specifically [Method 3: Connect from the terminal via SSH CLI](https://docs.aws.amazon.com/sagemaker/latest/dg/remote-access-local-ide-setup.html#remote-access-local-ide-setup-local-vs-code-method-3-connect-from-the-terminal-via-ssh-cli).

Make the script executable:

```bash
chmod +x /path/to/bootstrap/aws/sagemaker_connect.sh
```

Configure $HOME/.ssh/config to add the following entry:

```bash
Host space-name
  HostName 'arn:PARTITION:sagemaker:us-east-1:111122223333:space/domain-id/space-name'
  ProxyCommand '/path/to/bootstrap/aws/sagemaker_connect.sh' '%h' AWS_PROFILE_NAME
  ForwardAgent yes
  AddKeysToAgent yes
  StrictHostKeyChecking accept-new
```

Breakdown of the `HostName`:
- 'arn:PARTITION:sagemaker:us-east-1:111122223333:space/domain-id/space-name'

For example, the PARTITION can be aws.

If you need to use a [named AWS credential profile](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html#cli-configure-files-using-profiles), change the proxy command as follows:

```bash
ProxyCommand '/path/to/bootstrap/aws/sagemaker_connect.sh' '%h' YOUR_CREDENTIAL_PROFILE_NAME
```

Connect via SSH or run SCP command:

```bash
ssh space-name
scp file_abc space-name:/tmp/
```

### Vast On-Start (`bootstrap/vast/onstart.sh`)

Use this script as the on-start bootstrap for Vast instances.
