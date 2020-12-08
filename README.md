
Project name:
===================================

CMPUT404-project-socialdistribution

See `project.org` for a description of the project.

Make a distributed social network!



Example Accounts
=================

Email: root@admin.com

Password:root


Description:
===================================

we are building a distributed social networking which interconnected and peer to peer.   This blogging/social network platform will allow the importing of other sources of posts (github, twitter, etc.) as well allow the distributing sharing of posts and content. An author sitting on one server can aggregate the posts of their friends on other servers.

Table of Contents:
===================================

[Design Document](https://github.com/returnturn/200OK/wiki/Design-Document)

[Glossary](https://github.com/returnturn/200OK/wiki/Glossary)

[Requirement Specification](https://github.com/returnturn/200OK/wiki/Requirement-Specification)

Installation:
=============

This section described how to set up your environment in you local computer. The software can only run if your environment set up properly, so be careful of it.

##  Dependency & Tools Installation 

#### virthualenv (the virtual environment for python)
```
$ pip install virtualenv
```
#### download the project,

```
$ git clone https://github.com/returnturn/200OK cmput404-project
```

#### Activate Virtual Environment

```
$ cd cmput404-project
$ virtualenv venv python=python3
$ venv\bin\activate
```
#### Download all dependencies

```
$ sudo pip install -r requirements.txt
```

#### Run server

```
$ python manage.py runserver
```

Usage
=====

 ### Login
    http://127.0.0.1:8000
 
 ### Sign Up
    http://127.0.0.1:8000/accounts/register/
  
 ### Public Posts List Without authentication
    http://127.0.0.1:8000/posts/

 ### Author Profile 
    http://127.0.0.1:8000/accounts/author/profile/{author_id}
    
 ### Author Friend List
    http://127.0.0.1:8000/author/{author_id}/friends/
    
 ### Author Posts
    http://127.0.0.1:8000/author/{author_id}/posts/
 
 ### Swagger Document For API
    http://127.0.0.1:8000/swagger-docs/ 
    However, we did not finish all requests and response in phase 1.
    Will finish in next phase
 
Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Karim Baaba
    Ali Sajedi
    Kyle Richelhoff
    Chris Pavlicek
    Derek Dowling
    Olexiy Berjanskii
    Erin Torbiak
    Abram Hindle
    Braedy Kuzma
    
Team: CMPUT404W20T07 [H03]
===================================

* Yuanmao Zhu    -    [yuanmao](https://github.com/yuanmaoChris)
* Leo Hong    -    [lhong2](https://github.com/returnturn)
* Yuhang Ma -    [yuhang5](https://github.com/yuhang5)
* Yipu Chen    -    [yipu1](https://github.com/YipuChen)
* Tianxin Ma      -    [tianxin3](https://github.com/tianxin3)
