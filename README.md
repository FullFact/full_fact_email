# Email interface for Full Fact

This reads email and saves it in the *haystack* format. Haystack is the XML format the fact checking tools use.

# User guide

We use this so an IMAP email account can subscribe to sources such as campaign mailing lists.

It runs as a stand-alone program or as a Python function. 

It reads message text (plain text and HTML) and pdf attachments. It ignores anything else. For example word documents or images of scanned text are not processed.

```
usage: email_haystack.py [-h] [-s SEARCH] [-v] [-p PASSWORD] [--user USER]
                         [--port PORT] [--host HOST]

Read emails from an imap mailbox and convert them to haystack xml.

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCH, --search SEARCH
                        Selection criterion. Normally ALL or UNSEEN. It
                        accepts any IMAP search spec See:
                        https://tools.ietf.org/html/rfc3501#section-6.4.4
  -v, --verbose
  -p PASSWORD, --password PASSWORD
                        Password for the email account
  --user USER           The user name to login to the email accout (normally
                        the email address) Defaults to the config value
  --port PORT           The IMAP port number defaults to the config value
  --host HOST           The host server defaults to the config value
```

IMAP search specs are flexible: for exmaple you could get all email in a date range which you have replied to.

Although you can enter the password on the command line, it's better to use the EMAIL_PASSWORD environmental variable. Command lines can become visible to hackers, e.g. through your history or process monitoring tools.

# Maintenance 

The config file email_haystack_config.py includes email account details and a pattern for creating output file names. The *save_file* parameter is typically something like './email_haystack/haysatck_email_{}.xml'; the placeholder parameter is the unique email ID. The unique email ID is also used as the Uniform Resource Indicator (URI) in the xml.

PDF processing relies on the free utlilty **pdftotext**. This is normally available on linux stystems. On Windows, it installs as part of the default git installation.

Emails often repeat the same information more than once, for exampmple as formatted text with a plain text alternative. The output will include all copies. The sentence recognition code will not always make the same decisions on where to split them.
