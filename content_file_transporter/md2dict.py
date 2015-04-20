#coding=utf-8
import re
import ast

def md_to_dict(md_file):
    md_pattern = r"(\n)*/\*(\n)*(?P<meta>(.*?\n)*?)\*/\n"
    md_pattern = re.compile(md_pattern)
    m = md_pattern.match(md_file)
    content = md_file[m.end():]
    meta = m.group("meta").split("\n")

    rv = dict()
    rv["meta"] = dict()
    for item in meta:
        if item:
            t = item.split(":")
            if len(t) == 2:
                try:
                    rv['meta'][t[0].lower()] = ast.literal_eval(t[1].strip())
                except Exception as e:
                    rv['meta'][t[0].lower()] = t[1].strip()
    rv['content'] = content
    return rv

if __name__ == "__main__":
    f = open("test.md", "r")

    print md_to_dict(f.read())
