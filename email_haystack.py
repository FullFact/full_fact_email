from imaplib import IMAP4_SSL
import email
from haystack import Meta, Haystack
import re
import email_haystack_config as config
from xml.etree import ElementTree 
import bs4 # Beautiful Soup
from nltk.tokenize import sent_tokenize

# TODO:  How to get only unread emails
# (_, data) = CONN.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com".strip()))
# https://coderwall.com/p/gorteg/python-s-imaplib

def gen_payload(msg):
    """
    A generator for breaking the payload into sentence like text
    
    It silently discards anything which isn't HTML or text
    """
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            for line in re.split('\.|\n{2+}', part.get_payload()):
                yield line
        elif part.get_content_type() == 'text/html':
            soup = bs4.BeautifulSoup(part.get_payload(), 'html.parser')
            for chunk in soup.strings:
                for line in sent_tokenize(chunk):
                    yield line

                    
def make_filename(message_id):
    """
    Convert a message ID into a filename based on the config

    The message ID is guaranteed unique but contains unsuitable characters.
    """
    keepcharacters = ' .-_'
    msg_id = "".join(
        c 
        for c in message_id 
        if c.isalnum() or c in keepcharacters
    ).rstrip()

    return config.save_file.format(msg_id)


def write(msg):
    attributes = {
        "publication": config.user,
        "pdate": email.utils.parsedate_to_datetime(msg['Date']).isoformat(),
        "author": msg['From'],
        # "authorname": None,
        "url": msg['Message-ID'],
    }
    hay = ElementTree.Element('haystack')
    meta = ElementTree.SubElement(hay, 'meta', attributes)
    for s in gen_payload(msg):
        s_element = ElementTree.SubElement(meta, 's')
        s_element.text = s

    doc = ElementTree.ElementTree(hay)
    doc.write(make_filename(msg['Message-ID']), 'UTF-8')
    

with IMAP4_SSL(host=config.host, port=config.port) as mbox:
    mbox.login(config.user, config.password)
    m = mbox.select()
    result, data = mbox.search(None, 'ALL')
    assert result == 'OK', result

    for num in data[0].split():
        kind, data = mbox.fetch(num, '(RFC822)')
        assert kind == 'OK', kind
        # print(data)
        protocol, content = data[0]
        msg = email.message_from_bytes(content)

        write(msg)