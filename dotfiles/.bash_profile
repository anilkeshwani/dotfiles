source ~/.bashrc

eval "$(/opt/homebrew/bin/brew shellenv)"
export BASH_SILENCE_DEPRECATION_WARNING=1
. "$HOME/.cargo/env"

# >>> juliaup initialize >>>

# !! Contents within this block are managed by juliaup !!

case ":$PATH:" in
*:/Users/anilkeshwani/.juliaup/bin:*) ;;

*)
    export PATH=/Users/anilkeshwani/.juliaup/bin${PATH:+:${PATH}}
    ;;
esac

# <<< juliaup initialize <<<

# Ruby
source /opt/homebrew/opt/chruby/share/chruby/chruby.sh
source /opt/homebrew/opt/chruby/share/chruby/auto.sh
chruby ruby-3.1.3
