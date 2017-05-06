# -*- coding: utf-8 -*-
"""
Created on Sat May  6 15:24:07 2017

@author: Michael

TODO: Store date and time as datetime.date and datetime.time types
"""

import io

class Meta:
    def __init__(self,
        publication = None,
        pdate = None,
        ptime = None,
        author = None,
        authorname = None,
        url = None,
        ):
        self.publication = publication
        self.pdate = pdate
        self.ptime = ptime
        self.author = author
        self.authorname = authorname
        self.url = url

    def __str__(self):
        ret = io.StringIO()
        ret.write("<meta")
        ret.write
        if self.publication is not None:
            ret.write(' publication = "' + self.publication + '"' )
        if self.pdate is not None:
            ret.write(' pdate = "' + self.pdate + '"' )
        if self.ptime is not None:
            ret.write(' ptime = "' + self.ptime + '"' )
        if self.author is not None:
            ret.write(' author = "' + self.author + '"' )
        if self.authorname is not None:
            ret.write(' authorname = "' + self.authorname + '"' )
        if self.url is not None:
            ret.write(' url = "' + self.url + '"' )
        ret.write("/>\n")
        return ret.getvalue()

class Haystack:
    def __init__(self):
        self.meta = []
        
    def __str__(self):
        ret = io.StringIO()
        ret.write('<haystack>')
        for m in self.meta:
            ret.write(str(m))
        ret.write('</haystack>')
        return ret.getvalue()


if __name__ == "__main__":
    h = Haystack()
    print(h)

    h.meta.append(Meta())
    h.meta.append(Meta(
        publication = "Dodgy Data Source",
        pdate = "2002-09-24",
        ptime = "09:00:00",
        author = "urn:example:org",
        authorname = "Aema Deseava",
        url = "http://trustme.com",
    ))
    print(h)
