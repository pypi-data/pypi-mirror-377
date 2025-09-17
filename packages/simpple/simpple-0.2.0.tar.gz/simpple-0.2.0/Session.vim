let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/repos/astro/simpple
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
set shortmess+=aoO
badd +13 ~/repos/astro/simpple/line.yaml
badd +44 docs/tutorials/getting-started.ipynb
badd +9 ~/repos/astro/simpple/load_yaml.py
badd +1 /usr/lib64/python3.13/site-packages/yaml/__init__.py
badd +73 ~/repos/astro/simpple/docs/tutorials/fitting-a-line.ipynb
badd +235 src/simpple/distributions.py
badd +30 ~/repos/astro/simpple/src/simpple/load.py
badd +71 ~/repos/astro/simpple/docs/tutorials/writing-model-classes.ipynb
argglobal
%argdel
edit ~/repos/astro/simpple/line.yaml
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
wincmd _ | wincmd |
vsplit
wincmd _ | wincmd |
vsplit
2wincmd h
wincmd w
wincmd w
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '1resize ' . ((&lines * 49 + 36) / 73)
exe 'vert 1resize ' . ((&columns * 106 + 159) / 319)
exe '2resize ' . ((&lines * 49 + 36) / 73)
exe 'vert 2resize ' . ((&columns * 106 + 159) / 319)
exe '3resize ' . ((&lines * 49 + 36) / 73)
exe 'vert 3resize ' . ((&columns * 105 + 159) / 319)
exe '4resize ' . ((&lines * 21 + 36) / 73)
argglobal
setlocal foldmethod=expr
setlocal foldexpr=v:lua.vim.treesitter.foldexpr()
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=99
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
4
sil! normal! zo
10
sil! normal! zo
let s:l = 1 - ((0 * winheight(0) + 24) / 49)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 02|
wincmd w
argglobal
if bufexists(fnamemodify("~/repos/astro/simpple/docs/tutorials/fitting-a-line.ipynb", ":p")) | buffer ~/repos/astro/simpple/docs/tutorials/fitting-a-line.ipynb | else | edit ~/repos/astro/simpple/docs/tutorials/fitting-a-line.ipynb | endif
if &buftype ==# 'terminal'
  silent file ~/repos/astro/simpple/docs/tutorials/fitting-a-line.ipynb
endif
setlocal foldmethod=expr
setlocal foldexpr=v:lua.vim.treesitter.foldexpr()
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=99
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
15
sil! normal! zo
20
sil! normal! zo
46
sil! normal! zo
let s:l = 74 - ((9 * winheight(0) + 24) / 49)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 74
normal! 0
wincmd w
argglobal
if bufexists(fnamemodify("~/repos/astro/simpple/docs/tutorials/writing-model-classes.ipynb", ":p")) | buffer ~/repos/astro/simpple/docs/tutorials/writing-model-classes.ipynb | else | edit ~/repos/astro/simpple/docs/tutorials/writing-model-classes.ipynb | endif
if &buftype ==# 'terminal'
  silent file ~/repos/astro/simpple/docs/tutorials/writing-model-classes.ipynb
endif
setlocal foldmethod=expr
setlocal foldexpr=v:lua.vim.treesitter.foldexpr()
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=99
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
29
sil! normal! zo
34
sil! normal! zo
35
sil! normal! zo
38
sil! normal! zo
40
sil! normal! zo
let s:l = 77 - ((24 * winheight(0) + 24) / 49)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 77
normal! 0150|
wincmd w
argglobal
if bufexists(fnamemodify("term://~/repos/astro/simpple//104063:/usr/bin/zsh;\#toggleterm\#1", ":p")) | buffer term://~/repos/astro/simpple//104063:/usr/bin/zsh;\#toggleterm\#1 | else | edit term://~/repos/astro/simpple//104063:/usr/bin/zsh;\#toggleterm\#1 | endif
if &buftype ==# 'terminal'
  silent file term://~/repos/astro/simpple//104063:/usr/bin/zsh;\#toggleterm\#1
endif
balt ~/repos/astro/simpple/load_yaml.py
setlocal foldmethod=expr
setlocal foldexpr=v:lua.vim.treesitter.foldexpr()
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=99
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
let s:l = 787 - ((20 * winheight(0) + 10) / 21)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 787
normal! 0
wincmd w
3wincmd w
exe '1resize ' . ((&lines * 49 + 36) / 73)
exe 'vert 1resize ' . ((&columns * 106 + 159) / 319)
exe '2resize ' . ((&lines * 49 + 36) / 73)
exe 'vert 2resize ' . ((&columns * 106 + 159) / 319)
exe '3resize ' . ((&lines * 49 + 36) / 73)
exe 'vert 3resize ' . ((&columns * 105 + 159) / 319)
exe '4resize ' . ((&lines * 21 + 36) / 73)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
