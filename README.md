# Peon

![Peon](/../assets/banner.jpg?raw=true)

### Let the front development back to the pastoral era ...

### 讓前端開發回歸田園時代 ...

<br>
<br>

## Concept 概念

Peon is for build, watching and packing web base front-end project while in develop.

這個項目叫做苦工... 很顯然，這個名字來自著名游戏裡面那种农民。苦工適用於網頁前端項目開發，它能夠用來構建、監控和打包前端項目。

Features for now:

1. Start develop server with SimpleHTTPServer or `Pyco`.
2. Automaticlly watch and build files. etc., html, css, coffee, less, sass...
3. Combine and compress project by configurable tasks.
4. Packing theme and upload to target api.


功能特性：
1. 啟動基於 Python SimpleHTTPServer 的開發服务器（或者啟動Pyco，不知道這是什麼的話，先別問了...）。
2. 自動監控和構建項目文件。例如：html, css, coffee, less, sass...
3. 通過配置文件組合和壓縮項目。
4. 打包主題並且可以上傳到指定的API。


Planning to do:
* Automatically create project folders, like or not.
* Automatically translate ES7 to ES6 to ES5 ... very two.

計畫中的新特性：
* 自動生成我認為好的前端項目結構，愛用不用吧 ...
* 自動把ES7轉ES6轉ES5 ... 好二 ...

============================

## Why Peon?

Basically Nodejs might install hundreds related package before write any code, Peon is much more easier cheap and effective ...

Some basic js package will call by subprocess, such as coffee-script less and uglify-js.

BTW, Peon may not suppport ***Windows***, It's untested, also not supported by python 3.0.

## 為什麼用Peon？

如果你不想开发一个前端项目时，碰了一下就要npm几百个依赖库；也不想因为某一个源版本依赖变化导致构建失败；不想动不动就要面对一个自称是“未来”，但过不多久又死掉的项目；那么这个项目能够帮你的前端开发工作免除这些烦恼。


## Installation

```sh setup.sh -p```
All required packages will install once for all. without ```-p``` param, will skip all required packages.

or

```sudo python setup.py install``` then install all required packages, both python pakcage and nodejs package manually.


## Usage
You have to place a 'peon.json' intro the project root folder first.
* peon.json: Config peon's tasks, see the example.

`peon [-s] [-c] [-w] [-z]`

### Config: peon.json

The config file is a JSON file named as `peon.json`. It must placed in same folder where to run this peon.

Most peon methods require this config file, but not all of it.

##### Common options:

src: source files path, could be a list. use 'glob' rules, with * or ? or Regex patterns.
*** glob not support **/* to search for all subfolder, there is custom funciton do recursive search ***
put ```!``` at first for exclude. make sure the exclude pattern is right level, because the reason above.

cwd: from dir.

dest: dest dir.


=======================
### -c: Construct

**`peon.json` is required.**

The param is action alias to define which taks group should be run.

Allowed action aliaes:

* 'init'
* 'build'
* 'release'
* 'construct'

Default is `release`.

If input action alias is not exists, then failback to 'construct'.

Put action alias into `peon.json` as key to define a tasks group.

```
{
  "init": {},
  "build": [],
  "release": [],
  "construct": {}
}
```

The value of action alias could be **[ dict ]** or **[ list:dict ]**. Each action can host multiple tasks.

#### Tasks:

`clean`: **[ str ]** or **[ list:str ]** , remove all given dirs.

`copy`: **[ list:dict ]**, copy files by given rules.
  * cwd: **[ str ]** from folder.
  * dest: **[ str ]** dest folder.
  * src: **[ list:str ]** files name with relative path.
  * flatten: **[ bool ]** copied files will place to dest folder as flatten.
  Default is False.
  * overwrite: **[ bool ]** overwrite copy if file is exists. default is True.

`render`: **[ dict ]**, rendering files by given rules.
  * cwd: **[ str ]** from folder.
  * dest: **[ str ]** dest folder. default is 'build' folder.
  * skip_includes: **[ list:str ]** file exts which will not process 'includes' behavior. for example, you don't want **jinja2** template includes be render by peon.
  * clean: **[ bool ]** clean dest folder before rendering.

`compress`: **[ list:dict ]**, compress rendered files.
  * type: **[ str ]** type of compress.
    1. `html`: compress html.
    2. `css`: compress css.
    3. `js`: compress js.
    4. `process_html`: process html between
    `<!-- build -->` and `<!-- /build -->`,
    such as `<!-- build:css replacement.. -->`, `<!-- build:js replacement... -->`, `<!-- build:[any_attrs] replacement.. -->`.
    5. `inline_angular_templates`: concat all ng templates into one file.
  * cwd: **[ str ]** from folder. default is 'dist' forlder.
  * src: **[ list:str ]** files name with relative path.
  * output: **[ str ]** output file name.
  * beautify: **[ bool ]** not uglify output file. default is `False`.
  * minify: **[ bool ]** minify when use `process_html`. default is `True`.
  * prefix: **[ str ]** prefix of ng template name,
  for `inline_angular_templates` only. default is `''`.
  * skip_includes: **[ bool ]** skip peon 'includes' files, default is `True`.
  (file name starts with '_').

`replace`: replace text.
  * cwd: **[ str ]** from folder. default is 'dist' folder.
  * src: **[ list:str ]** files name with relative path.
  * replacing: **[ list:dict ]** replacing rules.
    1. `from`: find this text.
    2. `to`: replace to this text.

`scrap`: remove files or dirs which is unnecessary.
  * cwd: **[ str ]** from folder. default is 'dist' folder.
  * src: **[ list:str ]** files name with relative path.

`rev`: revision with md5.
  * cwd: **[ str ]** from folder. default is 'dist' folder.
  * src: **[ list:str ]** files name with relative path.
  * find: **[ str ]** the revision pattern, must include text `<rev>`.


#### Construct config examples:

```
"init": {
  "copy": [
    {
      "name": "libs",
      "flatten": true,
      "src": [
        "angular/angular.js",
        "angular-cookies/angular-cookies.js",
        "angular-resource/angular-resource.js",
        "angular-animate/angular-animate.js",
        "angular-messages/angular-messages.js",
        "angular-aria/angular-aria.js",
        "angular-material/angular-material.js",
        "angular-route/angular-route.js",
        "angular-sanitize/angular-sanitize.js",
        "ng-file-upload/ng-file-upload.js"
      ],
      "cwd": "bower_components",
      "dest": "/src/scripts/libs/"
    },
    {
      "name": "css",
      "flatten": true,
      "src": [
        "angular-material/angular-material.css"
      ],
      "cwd": "bower_components",
      "dest": "/src/styles/"
    }
  ]
},
"build": {
  "clean": "build",
  "render": {
    "cwd": "src",
    "dest": "build"
  }
},
"release": [
  {
    "clean": ["dist", "build"],
    "render": {
      "cwd": "src",
      "dest": "build"
    },
    "copy": [
      {
        "name": "dist",
        "src": [
          "**/*",
          "!**/_*",
          "!_*"
        ],
        "cwd": "build",
        "dest": "dist"
      },
      {
        "name": "assets",
        "flatten": true,
        "src": [
          "**/*.ttf",
          "**/*.woff*",
          "**/*.png",
          "**/*.jpg",
          "**/*.svg"
        ],
        "cwd": "build",
        "dest": "dist"
      }
    ],
    "compress": [
      {
        "type": "inline_angular_templates",
        "src": [
          "blueprints/**/*.html",
          "common/**/*.html",
          "modals/**/*.html",
          "navs/**/*.html",
          "matters/**/*.html",
          "panels/**/*.html",
          "!**/_*.html"
        ],
        "cwd": "dist",
        "prefix": "",
        "beautify": false,
        "minify_includes": false,
        "output": "index.html"
      },
      {
        "type": "process_html",
        "cwd": "dist",
        "src": "*.html",
        "minify_includes": false
      },
      {
        "type": "html",
        "cwd": "dist",
        "src": "*.html"
      }
    ],
    "replace": {
      "src": [
        "*.min.*",
        "*.html"
      ],
      "cwd": "dist",
      "replacing": [
        {
          "from": "/styles/icons/svg",
          "to": "svg"
        },
        {
          "from": "icons/ico",
          "to": "ico"
        },
        {
          "from": "styles/logo.svg",
          "to": "logo.svg"
        }
      ]
    },
    "scrap": {
      "src": [
        "*",
        "!*.html",
        "!*.min.*",
        "!server_conf.js",
        "!*.png",
        "!*.jpg",
        "!*.svg",
        "!*.ttf",
        "!*.woff*"
      ],
      "cwd": "dist"
    },
    "rev": {
      "src": "*.html",
      "cwd": "dist",
      "find": "?md5=<rev>"
    }
  }
]
```


=======================
### -z: Packing

Make a zip package for all files in current folder, or specific folder.
You can also chose upload to a url.

**`peon.json` is required.**

action alis:

* 'packing':
  1. `zip`: pack files.
  2. `upload`: upload package file.


#### zip:

`zip`: **[ dict ]** packing files from folder.
  * cwd: **[ str ]** the folder need to be packing.
  * dest: **[ str ]** the folder to put the package zip file.
  * file: **[ str ]** the filename of zip file.
  * excludes: **[ list:str ]** excludes files when packing.
  * include_hidden: **[ bool ]** include hidden files or dir
  (starts with '.').

#### upload:

`upload`: **[ dict ]** upload package file to a url.
  * cwd: **[ str ]** the folder need to be packing.
  * file: **[ str ]** the filename of zip file.
  * headers: **[ dict ]** request headers.
  * params: **[ dict ]** request params.
  * data: **[ dict ]** request post data.
  * url: **[ str ]** the upload url.
  * delete: **[ str ]** delete the file after uploaded.


#### Packing config examples:

```
"packing": {
  "zip": {
    "cwd": "src",
    "dest": ".",
    "file": "theme.zip"
  },
  "upload": {
    "cwd": ".",
    "file": "theme.zip",
    "headers": {
      "SecretKey": "the_key_is_here"
    },
    "url": "the_url_is_here",
    "delete": true
  }
}
```

=======================

### -w: Watcher

Watch and rendering changes of files, also support host with a web server.

**`peon.json` is required.**

action alis:

* 'watch'

#### watch:

`watch`: **[ dict ]** upload package file to a url.
  * cwd: **[ str ]** the folder need to be watching.
  * dest: **[ str ]** the folder to output rendered.
  * clean: **[ bool ]** clean dest folder before watch.
  * server: **[ bool ]** start http web server.
  * port: **[ str ]** the port when start http web server.
  * pyco: **[ str ]** the pyco folder, than starts with pyco.
  * skip_includes: **[ list:str ]** file exts which will not process 'includes' behavior. for example, you don't want **jinja2** template


#### Watch config examples:

```
"watch": {
  "src": "src",
  "dest": "pyco/themes/default",
  "clean": true,
  "server": false,
  "pyco": "pyco",
  "skip_includes": "html"
}
```

=======================

### -s: Server

** cli **

Start web server wich cli.

`peon [-s port] [--dir dir]` or just `peon`

`-s port`: server port. default is 9527

`--dir dir`: folder you want start as server host. must be sub of current working dir.

=======================


### Include files pattern.

`_` Local files, Render all files in same folder.

`__` Parent files, Render all files in same folder and sub folders.

`_g_` Global files, Render all files from watched folder include sub folders.

`_r_` Root files, Render all files from root folder.

`__init__` Init files, Render all files from root folder.


=======================

#### TMPL file

files with `.tmpl` is TMPL file, those file will render to `{% templates %}`.
Mostly for rich html application.

