# Peon

A front-end constructing helper.
Peon is much week than grunt, he can only set on task at once.
He is better work with shell script.

==============
We build peon is becuase we are python project team, sometime grunt or gulp have to do some tricky things to full fill our needs, that's too hard for us, but python is much more easier...

## Files

* peon.json: Config peon's tasks, see the example.
* peon.py: Primary program.
* peon.sh: A shell script to help your understand how work together with your project.
* install.sh: install to global, mac and linux only, require 'sudo'.


## Usage
You have to place a 'peon.json' intro the project root folder first.


`peon.py [-r] [-c] [--rev] [--copy]`

=======================
-r or -rev: Revision to md5 by 'pattern' find in given files.

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
-c or -copy: Copy files from src to dest.

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

## Installation


#### Global 
`sudo sh install.sh` to install newest version as global.

Please note, don't forget make a peon.json in your project root.

#### Manually
Just copy those file intro your project.
