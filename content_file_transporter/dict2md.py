#coding=utf-8

sample = {"meta":{"title":"aaa","tag":['xcvxcv','老AA']},"content":"sdfsdfs\ndfxxx\nxx\n"}

def dict_to_md(data):
    meta = data.get("meta")
    content = data.get("content")

    meta_template = "{key}:{value}"
    meta = [meta_template.format(key=k.capitalize(), value=str(v)+"\n")
            for k, v in meta.iteritems()]

    meta = "".join(meta)

    file_content_template = "/*\n{meta}*/\n{content}"

    rv = file_content_template.format(meta=meta, content=content)
    return rv

if __name__ == "__main__":
    f = open("test.md", "w")
    f.write(dict_to_md(sample))
    f.close()