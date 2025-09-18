import os
import re
def fix(in_file,out_file):
    with open(in_file,'r') as f:
        content=f.read()

    pattern=r"(dependencies\s*=\s*\[)(.*?)(\])"
    match=re.search(pattern,content,re.DOTALL)
    if not match:
        print("No dependencies block found.")
        return

    start,deps_block,end=match.groups()

    fixed_lines=[]
    for line in deps_block.splitlines():
        line_stripped=line.strip()
        if not line_stripped:
            continue
        
        if not line_stripped.startswith('"') and not line_stripped.startswith("'"):
            line_stripped=f'"{line_stripped}"'

        if not line_stripped.endswith(','):
            line_stripped+=','
        fixed_lines.append("    " + line_stripped)


    fixed_block=start + "\n" + "\n".join(fixed_lines) + "\n" + end
    new_content=re.sub(pattern,fixed_block,content,flags=re.DOTALL)

    with open(out_file,'w') as f:
        f.write(new_content)
    print(f"[.] Fixed dependencies written to {out_file}")

fix("pyproject.toml", "pyproject_fixed.toml")