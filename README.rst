yet another txt2epub converter
==============================

the intention of this program is to allow one create a epub file from
a bunch of text files.

why another converter?
----------------------

the reason for wanting a converter?  my favourite newspaper comes in pdf format
and it is very well readable on a fast and bright and large and heavy
screen like for example an iPad, but it really is close to unreadable
on a small thing like a e-ink based eReader.

so I started looking at what one would need to produce a epub file and
it resulted that it's not all as obvious or simple as for one to want
to do this by hand, but also not that difficult if you have a computer.

I found a dead and not-too-readable google-code program with this name,
I thought I would give it a try here.  

later on I found some more libraries, but I was far enough in the process that I thought I would finish it anyway!

what this is based on
---------------------

* python as programming language
* jinja2 for producing output

the way it works
----------------

* invoke it with two parameters and some options
 - first parameter is the directory holding the files
 - second comes the destination epub file
* read all files from the input directory
* produce the `mimetype`
 - this is hard coded
* produce the `META_INF/container.xml`
 - it points always at `content/00_content.opf`
* produce the `content/content.opf`
 - metadata: if you pass --options, they go here
 - manifest: the files in the directory
 - spine: again the files in the directory
 - guide: empty (I would not know what to put here)
* convert the documents to valid html
* zip everything in the correct order
