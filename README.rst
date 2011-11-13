the intention of this program is to allow one create a epub file from
a bunch of text files.

the reason for wanting this?  my favourite newspaper comes in pdf format
and it is very well readable on a fast and bright and large and heavy
screen like for example an iPad, but it really is close to unreadable
on a small thing like a e-ink based eReader.

so I started looking at what one would need to produce a epub file and
it resulted that it's not all as obvious or simple as for one to want
to do this by hand, but also not that difficult if you have a computer.

I found a dead and not-too-readable google-code program with this name,
I thought I would give it a try here.

what I want to use:

* python as programming language
* jinja2 for producing output

the way it will work:

* invoke it with one parameter (the directory holding the files)
* it will produce a file named as the directory, .epub
* read all files from the input directory
* produce the `mimetype`
 * this is hard coded
* produce the `META_INF/container.xml`
 * it points always at `content/00_content.opf`
* produce the `content/content.opf`
 * metadata: if you pass --options, they go here
 * manifest: the files in the directory
 * spine: again the files in the directory
 * guide: empty (I would not know what to put here)
* convert the documents to valid html
* zip everything in the correct order

