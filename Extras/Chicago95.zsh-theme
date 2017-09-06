local ret_status="%(?:C:F)"
local ret_status_git="%(?:G:F)"
function __msdos_pwd() {
	local __path=$(pwd)
	echo $__path | tr '/' '\\'
}
function __get_prefix_chicago95_zsh() {
	if git rev-parse --git-dir > /dev/null 2>&1; then
		echo $ret_status_git;
	else
		echo $ret_status;
	fi
}	

PROMPT='$(__get_prefix_chicago95_zsh):$(git_prompt_info)$(__msdos_pwd)>'

ZSH_THEME_GIT_PROMPT_PREFIX="\\%{$fg[yellow]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_DIRTY="%{$reset_color%}\\%{$fg[red]%}dirty"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$reset_color%}\\%{$fg[green]%}clean"
