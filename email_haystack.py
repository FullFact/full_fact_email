import os
from imaplib import IMAP4_SSL
import email
import email_haystack_config as config
from xml.etree import ElementTree 
import bs4 # Beautiful Soup
from nltk.tokenize import sent_tokenize
import argparse
import subprocess


# TODO:  How to get only unread emails
# (_, data) = CONN.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com".strip()))
# https://coderwall.com/p/gorteg/python-s-imaplib

class Attachment:
    """
    Abstract base class for email attachments
    """
    def __init__(self, data, original_file_name):
        self.data = data
        self.original_file_name = original_file_name

        
    def save(self, base_file_name):
        base, _ = os.path.splitext(base_file_name)
        self.out_file_name = base + '.' + self.original_file_name
        
        with open(self.out_file_name, 'wb') as out_file:
            out_file.write(self.data)

    def get_text(self):
        """
        Sub classes implement this to convert their format into plain text.
        
        The return value is a str, i.e. utf8
        """
        pass


class PdfAttachment(Attachment):
    """
    PDF email attachment
    """
    def get_text(self):
        # This creates a file 
        subprocess.run(
            ['pdftotext', '-layout', self.out_file_name],
            check = True,
        )
        name, ext = os.path.splitext(self.out_file_name)
        text_file_name = name + '.txt'
        with open(text_file_name, encoding='latin1') as text_file:
            return text_file.read()


def gen_payload(msg, message_file_name):
    """
    A generator for breaking the payload into sentence like text
    
    It silently discards anything which isn't HTML or text
    message_file_name: Used as a basis for generating attachment file names
    """
    for part in msg.walk():
        try:
            content_type = part.get_content_type()
        
            payload = part.get_payload(decode = True)
            if  msg['Content-Transfer-Encoding'] == 'quoted-printable':
                payload = payload.decode()

            if content_type == 'text/plain':
                # Using NLTK to determine sentences works better than splitting.
                # For example splitting breaks up an URL.
                payload = part.get_payload(decode = True).decode()
                for line in sent_tokenize(payload):
                    yield line
            elif content_type == 'text/html':
                payload = part.get_payload(decode = True).decode()
                soup = bs4.BeautifulSoup(payload, 'html.parser')
                for chunk in soup.strings:
                    for line in sent_tokenize(chunk):
                        yield line
            elif content_type == 'application/pdf':
                original_file_name = part.get_filename()
                file_part = PdfAttachment(payload, original_file_name)
                file_part.save(message_file_name)
                text = file_part.get_text()
                for line in sent_tokenize(text):
                    yield line
            else:
                print('skipping', content_type)

        except:
            print(message_file_name)
            print('from:', msg['From'])
            print('Subject:', msg['Subject'])
            raise



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
    
    out_file_name = make_filename(msg['Message-ID'])

    hay = ElementTree.Element('haystack')
    meta = ElementTree.SubElement(hay, 'meta', attributes)
    for content in gen_payload(msg, out_file_name):
        s_element = ElementTree.SubElement(meta, 's')
        s_element.text = content

    doc = ElementTree.ElementTree(hay)
    doc.write(out_file_name, 'UTF-8')
    

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
        See: https://tools.ietf.org/html/rfc3501#section-6.4.4
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
