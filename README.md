# Peon

![Peon](/../assets/banner.jpg?raw=true)

### Let the front development back to the pastoral era ...

### 讓前端開發回歸田園時代 ...

<br>
<br>

## Concept 概念

The project is call Peon. Obviously the name idea is form a famous cat. Peon is for build, watching and packing web base front-end project while in develop.

這個項目叫做苦工... 很顯然，這個名字來自著名游戏裡面那种农民。苦工適用於網頁前端項目開發，它能夠用來構建、監控和打包前端項目。

Features for now:

1. Start develop server with SimpleHTTPServer or `Pyco`.
2. Automaticlly watch and build files. etc., html, css, coffee, less, sass...
3. Combine and compress project by configurable tasks.
4. Packing theme and upload to target api.


現有特性：
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

## 為什麼用苦工？

如果你不想開發一個前端項目就要拽一百多個依賴庫，不想因為一個源版本跟錯誤導致啟動失敗，不想動不動就要面對一個冒出來將會是“未來”的項目，那麼希望這個項目能夠幫你的前端開發工作專注在交互和呈現上。


## Installation
```sudo python setup.py install```

or

```sh setup.sh```

You can run ```sh setup.sh -p``` to install all required packages once for all.
without ```-p``` param, packages will skiped.

## Usage
You have to place a 'peon.json' intro the project root folder first.
* peon.json: Config peon's tasks, see the example.

`peon [-s] [-c] [-w] [-t] [-z]`

=======================
### -c: Construct

Must with a peon.json in same folder when run this command.

command with param could help define which action you want to run.

Allow action params

* 'construct'
* 'init'
* 'build'
* 'release'

Default is ```release``` (because this action is most often.)

action is not related with task, you can run any task in any type aciton.
As I said action is only help you define what you want to do.


======================

##### common config options

src: Source files path, could be a list. use 'glob' rules, with * or ? or Regex patterns.
*** glob not support **/* to search for all subfolder, there is custom funciton do recursive search ***
put ```!``` at first for exclude. make sure the exclude pattern is right level, because the reason above.

cwd: Root dir of file path.

dest: Dest for copy files.


##### task: Copy

Copy files from src to dest.

```
  "copy": [
    {
      "name": "libs"
      "flatten": true,
      "src":[
        "lodash/dist/lodash.js",
        "angular/angular.js",
        "*/*/*.js",
        "!*/*.html"
      ],
      "cwd":"bower_components/",
      "dest":"src/libs"
    }
  ]
```
copy: The key of task options.

<group>: A group name of copy files. 'libs' is group name in the sample above. usual define different package. You can define multiple groups with different options. and you have to make different group name by your self.

`flatten`: Those files will not keep their folder while copy to the dest.

`force`: Replace file if exist. default is True.

##### task: Clean

Clean folders before do anything else.

```
  "clean": ["dist"]

```

Put dir names into this option, could be single string or list contain strings.

##### task: Scrap

Detele files with rules. Use that after compress task to remove useless files or dirs.

```
  "scrap": {
    "src":[
      "*.js",
      "*.html",
      "styles/*.png",
      "!*.min.*",
      "!*.png",
      "!index.html"
    ],
    "cwd":"dist"
  }
```

##### task: Replace

Replace string with pattern

```
  "replace": {
    "src": "*.min.*",
    "cwd": "dist",
    "replacing": [
      {
        "from": "/styles/icons/svg",
        "to": "svg"
      }
    ]
  }

```

`replacements`: replace rules, support string only no regex yet.


##### task: Render

Render files from source dir to dest dir

```
  "render":{
    "cwd": "src",
    "dest": "build",
    "clean": true,
    "skip_includes":[]
  }

```

`clean`: clean a dest folder before rendering

`skip_includes`: skip those file types from include rendring. If the type is 'html',
the {% include ... %} will not effect.


##### task: Compress

Compress files, minify css js html, and process html, and able to concat angular templates.

```
  "compress": [
    {
      "type": "inline_angular_templates",
      "src": [
        "blueprints/**/*.html",
        "modals/**/*.html",
        "!**/_*.html"
      ],
      "cwd": "dist",
      "prefix": "",
      "beautify": false,
      "allow_includes": false,
      "output":"index.html"
    },
    {
      "type": "process_html",
      "minify": true,
      "cwd": "dist",
      "src": "*.html"
    },
    {
      "type": "html",
      "cwd": "dist",
      "src": "*.html"
    }
  ]

```

Compress task include multiple groups. The group's key can be custom to any latin name.

```
  {
    "type": "process_html",
    "cwd": "dist",
    "src": "*.html"
  }

```

`type`: define compress type. `html` `css` `js` `process_html` `inline_angular_templates`.

type [inline_angular_templates]:

- `prefix`: define ng templates id prefix, etc., '/'. this is for match the template reference.
- `allow_includes`: set it true will concat include files (starts or ends with '_'), default is False.
- `beautify`: define output templates is minifed or readable.
- `output`: file you want fill template script into. `<!-- ng-templates -->` mark must somewhere in this file.


type [css, js]:

- `type`: the type of file you want to process.
- `cwd`: the root dir you work in.
- `src`: the file you want minify will output it self.
- `beautify`: define output file is minifed or readable.
- `output`: the file name you want output to minified file.


type [html]:

*html don't need output or beautify, if beautify just same as it self.*

- `type`: the type of file you want to process.
- `cwd`: the root dir you work in.
- `src`: the file you want minify will output it self.


type [process_html]

- `type`: the type of file you want to process.
- `cwd`: the root dir you work in.
- `src`: the file you want minify will output it self.
- `beautify`: define output file is minifed or readable.

##### task: Rev

Revision to md5 by 'pattern' find in given files.
Use it after grunt relese, because grunt litte bit hard to convert md5 filename.

```
  "rev":{
    "src":"/*.html",
    "cwd":"release/",
    "find":"?md5=<rev>"
  }
```
rev: The key of task options.

src: Source file path.

cwd: Root dir of file path.

find: Peon will find those string and replace `<rev>` with that string.



=======================
### -z:  Packing

Make a zip package for all files in current folder, or specific folder.
You can also chose upload to a restapi.

##### task: Zip

*** This cmd can runing with our peon.json tasks.

***cli:*** `--exclude` for exclude files pattern.

```
  "zip": {
    "cwd":null,
    "file":null,
    "include_hidden":false,
    "include_peon_config":false,
    "excludes":[]
  }

```
`cwd` the dir path you want to packing

`file` file name you want to specific. default is current folder name.

`include_hidden` include start with '.'.

`include_peon_config` include 'peon.json'.

`excludes` excludes files as list. pattern supported.

##### task: Upload

*** This cmd can only work with peon.json tasks.
make sure there is `zip` task before, otherwise will get a error.

```
  "upload": {
    "cwd":null,
    "file":null,
    "headers":{
      "SecretKey":"1d02aa814dc64db3a6494624ca35a03a"
    },
    "url":"http://localhost:5000/app/test/develop/theme",
    "data":null,
    "params":null
  }

```
`cwd` the dir path you want to upload

`file` file name you want to upload. default is current folder name.

`headers` anything you need put intro headers.

`url` request api url.

`data` request data

`params` request params


## -w: Watcher
```
  "watch":{
    "src": "src",
    "dest": "build",
    "skip_includes":[],
    "init": true,
    "server": true,
    "port": 9527
  }
```

`peon` -w [init] [-s port] [--src src_dir] [--dest dest_dir] [--skip file_type]

`-w init`: start watcher, with keyword 'init' will clean dest dir before watching start.

`-s port`: start watcher will server. define port or default is 9527

`--src src_dir`: watcher will get source file from src folder.

`--dest dest_dir`: watcher will render file into dest folder.

`--skip`: watcher will skip a file type. this option can use multiple time for a list of file types.

Wactching Coffee jade less. If it's changed than compile a new file.
files start or end with undescore '_' is changed will compile all files but it self.

#### Prefix and settings

`_` Local files, Render all files in same folder.

`__` Parent files, Render all files in same folder and sub folders.

`_g_` Global files, Render all files from watched folder include sub folders.

`_r_` Root files, Render all files from root folder.


## -s: Server

`peon` [-s port]  [--dir dir] or just `peon`

`-s port`: server port. default is 9527

`--dir dir`: folder you want start as server host. must be sub of current working dir.

`peon` -s --http, start server with simplehttp directly.

`peon` -s --harp, start server with harp directly (no recommand, but you can do that if you need).
Please make sure you have node npm harp kind stuff ...
