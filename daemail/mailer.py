from   __future__  import unicode_literals
from   email.utils import formataddr
import locale
import platform
import subprocess
import traceback
from   .           import __version__
from   .message    import DraftMessage
from   .senders    import MboxSender
from   .util       import MailCmdError, mail_quote, nowstamp, rc_with_signal, \
                            show_argv

USER_AGENT = 'daemail {} ({} {})'.format(
    __version__, platform.python_implementation(), platform.python_version()
)

class CommandMailer(object):
    def __init__(self, sender, dead_letter, to_addr, to_name=None,
                 from_addr=None, from_name=None,
                 failure_only=False, nonempty=False, no_stdout=False,
                 no_stderr=False, split=False, encoding=None,
                 err_encoding=None, utc=False, mime_type=None):
        self.from_addr = from_addr
        self.from_name = from_name
        self.to_addr = to_addr
        self.to_name = to_name
        self.failure_only = failure_only
        self.nonempty = nonempty
        self.sender = sender
        self.no_stdout = no_stdout
        self.no_stderr = no_stderr
        self.split = split or mime_type is not None
        self.encoding = encoding
        self.err_encoding = err_encoding
        self.utc = utc
        self.mime_type = mime_type
        self.dead_letter = dead_letter
        if self.encoding is None:
            self.encoding = locale.getpreferredencoding(True)
        if self.err_encoding is None:
            self.err_encoding = self.encoding

    def run(self, command, *args):
        cmdstring = show_argv(command, *args)
        msg = DraftMessage()
        if self.from_addr is not None:
            msg.headers['From'] = formataddr((self.from_name, self.from_addr))
        msg.headers['To'] = formataddr((self.to_name, self.to_addr))
        msg.headers['User-Agent'] = USER_AGENT
        try:
            results = self.subcmd(command, *args)
        except Exception:
            msg.headers['Subject'] = '[ERROR] ' + cmdstring
            msg.addtext('An error occurred while attempting to run the command:'
                        '\n' + mail_quote(traceback.format_exc()))
        else:
            if results["rc"] == 0 and (self.failure_only or
                    self.nonempty and not (results["stdout"] or
                                           results["stderr"])):
                return
            if results["rc"] == 0:
                msg.headers['Subject'] = '[DONE] ' + cmdstring
            else:
                msg.headers['Subject'] = '[FAILED] ' + cmdstring
            results["rc"] = rc_with_signal(results["rc"])
            msg.addtext('Start Time:  {start}\n'
                        'End Time:    {end}\n'
                        'Exit Status: {rc}\n'.format(**results))
            # An empty byte string is always an empty character string and vice
            # versa, right?
            if results["stdout"]:
                msg.addtext('\nOutput:\n')
                if self.mime_type is not None:
                    msg.addmimeblob(results["stdout"], self.mime_type, 'stdout')
                else:
                    msg.addblobquote(results["stdout"], self.encoding, 'stdout')
            elif results["stdout"] is not None:
                msg.addtext('\nOutput: none\n')
            if results["stderr"]:
                # If stderr was captured separately but is still empty, don't
                # bother saying "Error Output: none".
                msg.addtext('\nError Output:\n')
                msg.addblobquote(results["stderr"], self.err_encoding, 'stderr')
        msgbytes = msg.compile()
        try:
            self.sender.send(msgbytes, self.from_addr, self.to_addr)
        except MailCmdError as e:
            msg.addtext(
                '\nAdditionally, the mail command {0!r} exited with return'
                ' code {1} when asked to send this e-mail.\n'
                .format(e.sendmail, rc_with_signal(e.rc))
            )
            if e.output:
                msg.addtext('\nMail command output:\n')
                msg.addblobquote(e.output, locale.getpreferredencoding(True),
                                 'sendmail-output')
            else:
                msg.addtext('\nMail command output: none\n')
        except Exception as e:
            msg.addtext(
                '\nAdditionally, an exception occurred while trying to send'
                ' this e-mail:\n' + mail_quote(traceback.format_exc())
            )
        else:
            return
        ### TODO: Handle failures here!
        MboxSender(self.dead_letter)\
            .send(msg.compile(), self.from_addr, self.to_addr)

    def subcmd(self, command, *args):
        params = {}
        if self.split or self.no_stdout or self.no_stderr:
            params = {
                "stdout": None if self.no_stdout else subprocess.PIPE,
                "stderr": None if self.no_stderr else subprocess.PIPE,
            }
        else:
            params = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        start = nowstamp(self.utc)
        p = subprocess.Popen((command,) + args, **params)
        # The command's output is all going to be in memory at some point
        # anyway, so why not start with `communicate`?
        out, err = p.communicate()
        end = nowstamp(self.utc)
        return {
            "rc": p.returncode,
            "start": start,
            "end": end,
            "stdout": out,
            "stderr": err,
            #"pid": p.pid,
        }
