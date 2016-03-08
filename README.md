# Peon

A front-end project develop helper.

1. Start dev server with SimpleHTTPServer or Harp.
2. Watching file changes for coffee less sass and jade.
3. Build/Compress static files by task config.
4. Create backups.
5. Packing and uploads (for our platform only).
6. Transport data so supmice system (for our platform only).

==============
Becuase grunt or gulp always can't full fill our needs, and custom nodejs scripts is too hard for me,
but python is much more easier...

Some basic node srcipt is call by subprocess, such as coffee-script jade less uglify-js.

BTW, may not suppport ***Windows***.

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


##### task: Install
Run bower install/update or npm install/update.
It's take long time, and the remote source may block by GFW.
I'ts better have people do it maunally.

```
  "install":["bower","npm"]
```

##### task: Copy

Copy files from src to dest.

```
  "copy": {
    "libs":{
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
  }
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
    "replacements": [
      {
        "pattern": "/styles/icons/svg",
        "replace": "svg"
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
  "compress": {
    "inline_angular_templates":{
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
    "process_html":{
      "type": "process_html",
      "minify": true,
      "cwd": "dist",
      "src": "*.html"
    },
    "html":{
      "type": "html",
      "cwd": "dist",
      "src": "*.html"
    }
  }

```

Compress task include multiple groups. The group's key can be custom to any latin name.

```
  "<group>":{
    "type": "process_html",
    "cwd": "dist",
    "src": "*.html"
  }

```

`type`: define compress type. `html` `css` `js` `process_html` `inline_angular_templates`.

type [inline_angular_templates]: 

- `prefix`: define ng templates id prefix, etc., '/'. this is for match the template reference.
- `beautify`: define output templates is minifed or readable.
- `allow_includes`: set it true will concat include files (starts or ends with '_'), default is False.
- `output`: file you want fill template script into. `<!-- ng-templates -->` mark must somewhere in this file.


type [css, js]:

- `output`: the file name you want output to minified file.


type [html]:

- `src`: the file you want minify will output it self.

type [process_html]

- `src`: the file you want minify will output it self.
- `minify`: minify white process html.

##### task: Rev

Revision to md5 by 'pattern' find in given files.
Use it after grunt relese, because grunt litte bit hard to convert md5 filename.

```
  "rev":{
    "src":"/*.html",
    "cwd":"release/",
    "find":"?md5=null",
    "pattern":"null"
  }
```
rev: The key of task options.

src: Source file path.

cwd: Root dir of file path.

pattern: Replacement pattern, peon will replace those string intro md5 code.

[optional]

find:  Specify the exact scope of a pattern. Peon will find those string and  replace pattern with that string.



=======================
### -z:  Packing

Make a zip package for all files in current folder, or specific folder.
You can also chose upload to a restapi.

##### task: Zip

*** This cmd can runing with our peon.json tasks. 

***cli:*** `--exclude` for exclude files pattern.

```
  "zip":{
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
  "upload":{
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


## -b: Backup
Backup file and db.

```
  "backup":{
    "redis":{
      "src":"/Users/redy/dump.rdb",
      "dbname":"dev",
      "dbhost":null,
      "port":null,
      "user":null,
      "pwd":null,
      "dest":null
    },
    "mongodb":{
      "dbname":"dev",
      "dbhost":null,
      "port":null,
      "user":null,
      "pwd":null,
      "src":null,
      "dest":null
    },
    "files":{
      "src":[
        "/Users/redy/deployment_data/",
        "/Users/redy/etc/nginx/sites-available/",
        "/Users/redy/etc/supervisor/conf.d/"
      ]
    }
  }

```

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



## -t : Transport

`peon` -t [upload] or `peon` -t [download] or `peon` -t [media]

Trassport pyco content file and site data to supmice system

'dest' or 'cwd' is define the content folder for upload or download.


```
  "transport":{
    "upload":{
      "cwd":".",
      "replace": [
        {
          "pattern":"[%uploads%]", 
          "replacement":"http://localstatic:5050/apps/redy/123123/uploads/"
        }
      ],
      "headers":{
        "SecretKey":"1d02aa814dc64db3a6494624ca35a03a"
      },
      "url":"http://localhost:5000/app/123123/develop/sitedata"
    },
    "download":{
      "dest":".",
      "replace": [
        {
          "pattern":"http://localstatic:5050/apps/redy/123123/uploads/", 
          "replacement":"[%uploads%]"
        }
      ],
      "headers":{
        "SecretKey":"1d02aa814dc64db3a6494624ca35a03a"
      },
      "url":"http://localhost:5000/app/123123/develop/sitedata"
    }
    "media": {
      "dest":"test/uploads",
      "suffix": null,
      "headers":{
        "SecretKey":"1d02aa814dc64db3a6494624ca35a03a"
      },
      "url":"http://api.sup.farm/app/website/develop/media"
    }
  }
```

`replace` for replace content and meta markers. etc., [%uploads%] is the shortcode for **pyco** uploads folder.

`url` upload api

`cwd` the content folder you want upload, for upload only.

`dest` the content folder you want download to, for download only.

`headers` request headers

`suffix` is for **media** only, sometime you want add suffix after the media src to get specific type. etc., 'original' suffix will get the original media.
'thumbnail' will get thumbnail.


*** Content sample ***
```
  content/
    content_type/
      somepage.md
      ...
    site.json
    index.md
    error_404.md
    somepage.md
    ...
    
```

*** Site.json smaple ***
```
{
  "meta": {
    "author": "redy",
    "copyright": "2015 © Soopro tech Co., Ltd.",
    "description": "...",
    "license": "#license",
    "locale": "en_US",
    "logo": null,
    "register": {
      "placeholder": "Email address for register",
      "text": "Free Register",
      "url": ""
    },
    "title": "Soopro",
    "translates": {
      "en_US": {
        "name": "English",
        "url": "#"
      },
      "zh_CN": {
        "name": "汉语",
        "url": "#"
      }
    }
  },
  "content_types": {
    "_feature": "Features",
    "_gallery": "Gallery",
    "page": "Pages"
  },
  "menus": {
    "primary": [
      {
        "alias": "home",
        "meta": {},
        "nodes": [],
        "title": "Back to home",
        "url": "/"
      },
      {
        "alias": "video",
        "meta": {},
        "nodes": [],
        "title": "Watch Video",
        "url": "/video"
      }
    ]
  },
  "terms": {
    "category": [
      {
        "alias": "inneral",
        "meta": {
          "parent": "",
          "pic": ""
        },
        "priority": 0,
        "title": "INNERAL"
      },
      {
        "alias": "forign",
        "meta": {
          "parent": "",
          "pic": ""
        },
        "priority": 0,
        "title": "FORGIN"
      }
    ]
  }
}
```
