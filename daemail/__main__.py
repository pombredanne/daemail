from   __future__ import print_function, unicode_literals
import argparse
from   datetime   import datetime
import os
import sys
import traceback
from   daemon     import DaemonContext  # python-daemon
from   .          import __version__
from   .          import senders
from   .mailer    import CommandMailer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chdir', metavar='DIR', default=os.getcwd(),
                        help="Change to this directory before running")
    parser.add_argument('-D', '--dead-letter', metavar='FILE',
                        default='dead.letter',
                        help="Append undeliverable mail to this file")
    parser.add_argument('-e', '--encoding',
                        help='Set encoding of stdout and stderr')
    parser.add_argument('-E', '--err-encoding', help='Set encoding of stderr',
                        metavar='ENCODING')
    parser.add_argument('-f', '--from-addr', '--from', '--sender',
                        help='From: address of e-mail')
    parser.add_argument('-F', '--failure-only', action='store_true',
                        help='Only send e-mail if command returned nonzero')
    parser.add_argument('-l', '--logfile', default='daemail.log',
                        help='Append unrecoverable errors to this file')
    parser.add_argument('-m', '--mail-cmd', default='sendmail -t',
                        metavar='COMMAND', help='Command for sending e-mail')
    parser.add_argument('-M', '--mime-type', '--mime',
                        help='Send output as attachment with given MIME type')
    parser.add_argument('-n', '--nonempty', action='store_true',
                        help='Only send e-mail if there was output or failure')
    parser.add_argument('--no-stdout', action='store_true',
                        help="Don't capture stdout")
    parser.add_argument('--no-stderr', action='store_true',
                        help="Don't capture stderr")

    parser.add_argument('--smtp-host')
    parser.add_argument('--smtp-port', type=int)
    parser.add_argument('--smtp-username')
    parser.add_argument('--smtp-password')
    smtp_ssl = parser.add_mutually_exclusive_group()
    smtp_ssl.add_argument('--smtp-ssl', action='store_true')
    smtp_ssl.add_argument('--smtp-starttls', action='store_true')

    parser.add_argument('--split', action='store_true',
                        help='Capture stdout and stderr separately')
    parser.add_argument('-t', '--to-addr', '--to', '--recipient', '--rcpt',
                        help='To: address of e-mail', metavar='RECIPIENT')
    parser.add_argument('-V', '--version', action='version',
                                           version='daemail ' + __version__)
    parser.add_argument('-Z', '--utc', action='store_true',
                        help='Use UTC timestamps')
    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.smtp_host is not None:
        if args.smtp_ssl:
            cls = senders.SMTPSSender
        elif args.smtp_starttls:
            cls = senders.StartTLSSender
        else:
            cls = senders.SMTPSender
        sender = cls(args.from_addr, args.to_addr, args.smtp_host,
                     args.smtp_port, args.smtp_username, args.smtp_password)
    else:
        sender = senders.CommandSender(args.mail_cmd)

    mailer = CommandMailer(
        encoding=args.encoding,
        err_encoding=args.err_encoding,
        from_addr=args.from_addr,
        failure_only=args.failure_only,
        sender=sender,
        nonempty=args.nonempty,
        no_stdout=args.no_stdout,
        no_stderr=args.no_stderr,
        split=args.split,
        to_addr=args.to_addr,
        utc=args.utc,
        mime_type=args.mime_type,
    )

    try:
        with DaemonContext(working_directory=args.chdir, umask=os.umask(0)):
            mailer.run(args.command, *args.args)
    except Exception:
        # If this open() fails, die alone where no one will ever know.
        sys.stderr = open(args.logfile, 'a')
            ### TODO: What encoding do I use for this???
        print(datetime.now().isoformat(), 'daemail', __version__,
              'encountered an exception:', file=sys.stderr)
        traceback.print_exc()
        print('', file=sys.stderr)
        print('Configuration:', vars(mailer), file=sys.stderr)
        print('Chdir:', repr(args.chdir), file=sys.stderr)
        print('Command:', [args.command] + args.args, file=sys.stderr)
        print('', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
