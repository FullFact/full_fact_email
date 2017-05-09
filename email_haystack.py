from imaplib import IMAP4_SSL
import email
from haystack import Meta, Haystack
import datetime
from email.utils import parsedate_to_datetime
import re

host = 'imap.one.com'
port = 993
ssl = 'SSL/TLS'
user = 'full_fact@grazebrook.com'
password = 'Michael1'
save_file = './haysatck.xml'

# TODO:  How to get only unread emails
# (_, data) = CONN.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com".strip()))
# https://coderwall.com/p/gorteg/python-s-imaplib

def gen_payload(msg):
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            for line in re.split('\.|\n{2+}', part.get_payload()):
                yield line


with IMAP4_SSL(host="imap.one.com", port=port) as mbox:
    mbox.login(user, password)
    m = mbox.select()
    result, data = mbox.search(None, 'ALL')
    assert result == 'OK', result

    for num in data[0].split():
        kind, data = mbox.fetch(num, '(RFC822)')
        assert kind == 'OK', kind
        # print(data)
        protocol, content = data[0]
        msg = email.message_from_bytes(content)
        
        hay = Haystack()
        meta = Meta(
            publication = user,
            pdate = email.utils.parsedate_to_datetime(msg['Date']),
            author = msg['From'],
            authorname = None,
            url = msg['Message-ID'],
        )
        hay.meta.append(meta)

        for s in gen_payload(msg):
            hay.meta[0].s.append(s)
        
        print(hay)