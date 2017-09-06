local ret_status="%(?:C:F)"
function __msdos_pwd() {
	local __path=$(pwd)
	echo $__path | tr '/' '\\'
}
PROMPT='${ret_status}:$(git_prompt_info)$(__msdos_pwd)>'

local ret_status_git="%(?:G:F)"
ZSH_THEME_GIT_PROMPT_PREFIX="\b\b${ret_status_git}:\\%{$fg[yellow]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_DIRTY="%{$reset_color%}\\%{$fg[red]%}dirty"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$reset_color%}\\%{$fg[green]%}clean"
