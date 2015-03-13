# Peon

A front-end develop helper.

1. Start dev server with SimpleHTTPServer or Harp.
2. Watching file changes for coffee less and jade.
3. Build static files from task config.


==============
I build peon is becuase we are python project team, sometime grunt or gulp can't full fill our needs, custom nodejs scripts is too hard for my team, but python is much more easier...


## Usage
You have to place a 'peon.json' intro the project root folder first.
* peon.json: Config peon's tasks, see the example.

`peon [-s] [-c] [-w]`

=======================
### -c: - Construct

Must with a peon.json in same folder when run this command.

##### --rev: - Rev


Revision to md5 by 'pattern' find in given files.

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

##### --copy: - Copy

Copy files from src to dest.

```
  "copy": {
    "libs":{
      "flatten": true,
      "src":[
        "lodash/dist/lodash.js",
        "angular/angular.js",
        "**/**/*.js",
      ],
      "cwd":"bower_components/",
      "dest":"src/libs"
    }
  }
```
copy: The key of task options.

<group>: A group name of copy files. 'libs' is group name in the sample above. usual define different package. You can define multiple groups with different options. and you have to make different group name by your self.

src: Source file path.

cwd: Root dir of file path.

dest: Dest for copy files.

[optional]

flatten: Those files will not keep their folder while copy to the dest.

## Server

peon_server

peon_server --harp, because I trid to find some python libs to compiler jade coffee and less, nothing but sucks. So leave me no choice, harp is most easy way to get it done. Maybe I will add a simple static server base on Flask in near future. Why Flask?

Please make sure you have node npm harp kind stuff ...

## Installation
python setup.py install

