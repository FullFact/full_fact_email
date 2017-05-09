import os
from imaplib import IMAP4_SSL
import email
import re
import email_haystack_config as config
from xml.etree import ElementTree 
import bs4 # Beautiful Soup
from nltk.tokenize import sent_tokenize
import argparse

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


def write(msg, user):
    attributes = {
        "publication": user,
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
    

def mail_to_haystack(args):
    with IMAP4_SSL(host=args.host, port=args.port) as mbox:
        mbox.login(args.user, args.password)
        m = mbox.select()
        result, data = mbox.search(None, args.search)
        assert result == 'OK', result
    
        for num in data[0].split():
            kind, data = mbox.fetch(num, '(RFC822)')
            assert kind == 'OK', kind
            # print(data)
            protocol, content = data[0]
            msg = email.message_from_bytes(content)
    
            write(msg, args.user)

            
def command_line():
    parser = argparse.ArgumentParser(
        description="""
        Read emails from an imap mailbox and convert them to haystack xml.
        """
    )
    parser.add_argument(
        '-s', '--search',
        default='UNSEEN',
        help= """
        Selection criterion. Normally ALL or UNSEEN.
        It accepts any IMAP search spec
        See: https://tools.ietf.org/html/rfc3501#section-6.4.4'
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action = 'store_true',
    )
    parser.add_argument(
        '-p', '--password',
        default = os.getenv('EMAIL_PASSWORD'),
        help = """
        Password for the email account
        """
    )
    parser.add_argument(
        '--user',
        default = config.user,
        help = """
        The user name to login to the email accout (normally the email address)
        Defaults to the config value
        """
    )
    parser.add_argument(
        '--port',
        default = config.port,
        help = """
        The IMAP port number defaults to the config value
        """
    )
    parser.add_argument(
        '--host',
        default = config.host,
        help = """
        The host server defaults to the config value
        """
    )

    return parser.parse_args()

            
def main():
    args = command_line()
    mail_to_haystack(args)


if __name__ == '__main__':
    main()
