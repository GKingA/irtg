" Vim syntax file
" Language:	Man page
" Maintainer:	Kinga Gemes
" Version Info:
" Last Change:	2018 Aug 14

if exists("b:current_syntax")
    finish
endif

syn match rule ".* -> .*"

syn region interpretationName start="\[" end="\]"
syn region interpretation start="interpretation" end="\n"
syn region string start='"' end='"'
syn region string start="'" end="'"
syn region comment start="//" end="\n"

let b:current_syntax = "irtg"

hi def link rule        Statement
hi def link comment     Comment
hi def link interpretationName    PreProc
hi def link interpretation         Type
hi def link string      Constant
