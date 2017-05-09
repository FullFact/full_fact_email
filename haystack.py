# -*- coding: utf-8 -*-
"""
Created on Sat May  6 15:24:07 2017

@author: Michael

TODO: Store date and time as datetime.date and datetime.time types
"""

import io
import datetime

class Meta:
    def __init__(self,
        publication = None,
        pdate = None,
        author = None,
        authorname = None,
        url = None,
        ):
        self.authorname = authorname
        self.author = author
        self.publication = publication
        self.pdate = pdate
        self.url = url
        self.s = []

    def __str__(self):
        ret = io.StringIO()
        ret.write("<meta")
        ret.write
        if self.publication is not None:
            ret.write(' publication = "' + self.publication + '"' )
        if self.pdate is not None:
            ret.write(' pdate = "' + self.pdate.isoformat() + '"' )
        if self.author is not None:
            ret.write(' author = "' + self.author + '"' )
        if self.authorname is not None:
            ret.write(' authorname = "' + self.authorname + '"' )
        if self.url is not None:
            ret.write(' url = "' + self.url + '"' )
        ret.write('>\n')
        for sentence in self.s:
            ret.write('<s>' + sentence + '</s>\n')
        ret.write("<meta/>\n")
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
    assert str(h) == '<haystack></haystack>', repr(str(h))

    h.meta.append(Meta())
    h.meta.append(Meta(
        publication = "Dodgy Data Source",
        pdate = datetime.datetime(2017,5,6,16,30),
        author = "urn:example:org",
        authorname = "Aema Deseava",
        url = "http://trustme.com",
    ))
    for s in ["You must believe me", "there are 100 aliens on the moon"]:
        h.meta[1].s.append(s)

    assert str(h) == (
        "<haystack><meta>\n"
        "<meta/>\n"
        '<meta publication = "Dodgy Data Source" pdate = "2017-05-06T16:30:00" author = "urn:example:org" authorname = "Aema Deseava" url = "http://trustme.com">\n'
        "<s>\n"
        "You must believe me\n"
        "<s>\n"
        "<s>\n"
        "there are 100 aliens on the moon\n"
        "<s>\n"
        "<meta/>\n"
        "</haystack>"
    ), repr(str(h))

    print(h)
