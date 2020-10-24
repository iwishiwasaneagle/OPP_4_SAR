from pydriller import *
import os, io, subprocess, sys

cwd = os.getcwd()
gr = GitRepository(cwd)

last_commit_hash = ""

data = []

c = 0
for commit in RepositoryMining(cwd).traverse_commits():
    gr.checkout(commit.hash)
    
    proc = subprocess.Popen(['cloc', cwd, '--exclude-dir=venv,img', '--csv'], stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(proc.stdout, encoding='utf-8'):
        if "SUM" in line:
            txt = line.split(',')

            files = txt[0]
            blank = txt[2]
            comment = txt[3]
            code = txt[4]
            date = commit.committer_date.strftime("%a %d %b %H:%M:%S BST %Y")

            data.append((date,files,blank,comment,code))

            break
    print(f"{(c:=c+1)}/195",file=sys.stderr,end='\r')
    last_commit_hash = commit.hash
gr.checkout(last_commit_has)

print("".join([",".join(f) for f in data]))



