
# Dotty - Small and light Static Site Generator

## Why another Static Site Generator?

I love Static Site Generators. But I've only used a few, and whilst they are powerful, they can also be troublesome.

I started out with [Jekyll](https://jekyllrb.com) and I'll always have an affection for the SSG that got me hooked, but wrangling with Ruby and Gems means I regularly have issues when using it. Builds fail, Gem problems, Ruby versions - it feels like a House of Cards sometimes.

Recently, I've been using [Eleventy](https://11ty.io), and I really like it. It has the familiarity of Jekyll, but you can get moving with it so much faster. It's written in Node JS and that leads on to what I don't like about it; 160Mb of Node Modules. It's not Eleventy's fault. I have the same feeling about many Node tools and applications. Sometimes I just want to make a website with one or two pages, and that many Node Modules feels very heavy. In some ways it doesn't matter, because once they are installed then that's it really and the SSG generates sites really quickly, but it doesn't sit right with me.

I wanted to build my own, and I really like Python, so I thought I'd try.

Why Python? Well:

* Currently, it's the language I'm best at writing, and importantly, I enjoy writing in it.
* It's mature, stable, and versatile. You can do almost anything in Python.
* Static Site Generators run mostly on Linux-based machines, be it a Macbook, or an Ubuntu instance on a server or container. On Linux, Python comes as standard, so no need to install anything else except a few dependencies.

Why not use one of the existing Python Static Site Generators like [Pelican](https://getpelican.com)? Because it's a good project for me, and it's pretty simple to build. If anything goes wrong, I can address it. If I need an extra bit of functionality, I can try writing it. I can make I want or need it to be. And one of the things I want is to try and keep it lean. I have written a prototype of this, and 90% of what I need it to do can be written in under 10kb or data, which for me feels about right. 

## Getting Started

1. Create and enter a new project folder
    mkdir dotty-site && cd dotty-site

2. Write some markdown in a file
    echo -e "# Hello Dotty\n\nA very tiny website made with Dotty!" > index.md

3. Run Dotty
    dotty build

This will create all the websites pages in the `site` folder by default, but you can configure this to be any other location in the **dottyconfig.json** file.

## Configuration

Dotty does not need any specific configuration to run. If you have a folder with a single file, then Dotty will use defaults to generate the site.

Alternatively, you can set up a config file. Dotty looks for a file called `dottyconfig.json', and the configuration options within this file will override the default options. Also, you can specify new site level options to use elsewhere within your website.

## .dottyignore

The .dottyignore file allows you to add items for Dotty to ignore during the build.

By default, Dotty will look everywhere - in the current directory, it's subdirectories and their subdirectories, and if it finds anything with a .md or a .html extension, it will be included in the build.

There are some folders and files that are already ignored by Dotty. These are:

    defaultIgnores = ['layouts', 'node_modules','site','includes','README.md']

Anything in the .dottyignore file will be added to this list and ignored at build time.

N.B. asking Dotty to ignore 'templates' may mean your blog post 'Best Website Templates' will also be ignored.


