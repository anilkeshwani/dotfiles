# Set up Conda inc. main environment
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh &&
    bash miniconda.sh -b -u -p "${HAFH:-${HOME}}/miniconda3" &&
    "${HAFH:-${HOME}}"/miniconda3/bin/conda init bash &&
    export PATH="${HAFH:-${HOME}}/miniconda3/bin:${PATH}" &&
    rm -rf miniconda.sh

conda create --name main --clone base --copy

# Create new public-private keypair for use with Github
ssh-keygen -t ed25519 -C "anilkeshwani@hotmail.com"

# Install tools
sudo apt install tree
