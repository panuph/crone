import os
import threading
import subprocess
import datetime as dt
import logging as log
from dateutil import tz
from pyparsing import *
from optparse import OptionParser

def range_parser(pattern, begin, end):
    """Builds parser for something like: 1,2,3-5,*/2,*"""
    atom = Combine(Regex(pattern) + "-" + Regex(pattern)).setParseAction(
               lambda s, l, t: list(range(int(t[0].split("-")[0]), int(t[0].split("-")[1]) + 1))) | \
           Regex(pattern).setParseAction(
               lambda s, l, t: [int(t[0])]) | \
           Combine(Literal("*/").suppress() + Word(nums)).setParseAction(
               lambda s, l, t: list(range(begin, end + 1, int(t[0])))) | \
           Literal("*").setParseAction(
               lambda s, l, t: list(range(begin, end + 1)))
    return (StringStart() + atom + ZeroOrMore(Literal(",").suppress() + atom) + StringEnd()).setParseAction(
        lambda s, l, t: sorted(list(set(t))))

def datetime_parser(default):
    """Builds parser for datetime in format: YYYY-mm-ddTHH:MM:SS"""
    pattern = r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    format = "%Y-%m-%dT%H:%M:%S"
    atom = Regex(pattern).setParseAction(
               lambda s, l, t: dt.datetime.strptime(t[0], format)) | \
           Literal("*").setParseAction(
               lambda: dt.datetime.strptime(default, format))
    return StringStart() + atom + StringEnd()

def interval_parser(default=("d", 1)):
    """Builds parser for interval like: 1d"""
    atom = Combine(Word(nums) + "d").setParseAction(
               lambda s, l, t: ("d", int(t[0][:-1]))) | \
           Combine(Word(nums) + "h").setParseAction(
               lambda s, l, t: ("h", int(t[0][:-1]))) | \
           Combine(Word(nums) + "m").setParseAction(
               lambda s, l, t: ("m", int(t[0][:-1]))) | \
           Literal("*").setParseAction(
               lambda: default)
    return StringStart() + atom + StringEnd()

def timezone_parser(default="UTC"):
    """Builds parser for timezone like: Melbourne/Australia, UTC"""
    atom = Literal("*").setParseAction(lambda: default) | \
           Regex(".+")
    return StringStart() + atom + StringEnd()

def build_parsers():
    """Builds all required, ready-to-use parsing functions (in order)."""
    return (
        lambda x: list(range_parser(r"[0-5][0-9]|[0-9]", 0, 59).parseString(x)),
        lambda x: list(range_parser(r"2[0123]|[0-1]?[0-9]", 0, 23).parseString(x)),
        lambda x: list(range_parser(r"3[01]|[1-2][0-9]|0?[1-9]", 1, 31).parseString(x)),
        lambda x: list(range_parser(r"1[012]|[0]?[1-9]", 1, 12).parseString(x)),
        lambda x: list(range_parser(r"[0-6]", 0, 6).parseString(x)),
        lambda x: datetime_parser("2000-01-01T00:00:00").parseString(x)[0],
        lambda x: datetime_parser("2099-12-31T23:59:59").parseString(x)[0],
        lambda x: interval_parser().parseString(x)[0],
        lambda x: timezone_parser().parseString(x)[0]
    )

def total_seconds(td):     
    """Copied directly from python 2.7 datetime.timedelta.total_seconds()."""
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def exec_command(command, as_thread=False):
    """Executes the command, can be sequentially or concurrently."""
    if as_thread:
        threading.Thread(target=subprocess.check_call, args=(command,), 
            kwargs=dict(shell=True)).start()
    else:
        subprocess.check_call(command, shell=True)

def main(utcnow):
    parser = OptionParser("%prog [options]")
    parser.add_option("-p", "--path", 
        dest="path", default=os.path.join(os.path.expanduser("~"), ".cronetab"),
        help="path to the cronetab file (default is ~/.cronetab)")
    parser.add_option("-t", "--tzpath", 
        dest="tzpath", default="/usr/share/zoneinfo",
        help="path to the timezone directory (default is /usr/share/zoneinfo)")
    parser.add_option("--concurrent",
        dest="concurrent", default=False, action="store_true",
        help="run commands concurrently (default if False)")
    (options, args) = parser.parse_args()

    if not options.path or not os.path.exists(options.path):
        raise AssertionError("cronetab file %s not found" % options.path)

    # build parsing functions
    (minute, hour, date, month, day, begin, end, interval, timezone) = build_parsers()

    # process each line of command
    with open(options.path) as fd:
        log.info("<<<<< BEGIN >>>>>")
        for i, line in enumerate(fd):
            try:
                log.info("--- begin job %d ---", i + 1)
                # prepare the input line and skip if commented.
                log.info("input is %s", line.rstrip())
                if line.lstrip().startswith("#"):
                    log.info("skip this job as it is commented")
                    continue
                tokens = line.split()
                # check the path to the specified timezone
                tzfile = os.path.join(options.tzpath, timezone(tokens[8]))
                if not os.path.exists(tzfile):
                    log.error("timezone file %s does not exist", tzfile)
                    continue
                # calculate the current time at the timezone
                now = utcnow.astimezone(tz.tzfile(tzfile)).replace(tzinfo=None)
                log.info("now at %s is %s", timezone(tokens[8]), now)
                # check the minute condition
                if now.minute not in minute(tokens[0]):
                    log.debug("fail to meet minute condition")
                    continue
                # check the hour condition
                if now.hour not in hour(tokens[1]):
                    log.debug("fail to meet hour condition")
                    continue
                # check the date condition
                if now.day not in date(tokens[2]):
                    log.debug("fail to meet date condition")
                    continue
                # check the month condition
                if now.month not in month(tokens[3]):
                    log.debug("fail to meet month condition")
                    continue
                # check the day condition
                if now.isoweekday() % 7 not in day(tokens[4]):
                    log.debug("fail to meet day condition")
                    continue
                # check the period condition
                if not (begin(tokens[5]) <= now <= end(tokens[6])):
                    log.debug("fail to meet period condition")
                    continue
                # check the interval condition
                (key, value) = interval(tokens[7])
                diff = total_seconds(now - begin(tokens[5]))
                if key == "d":
                    if (diff / 86400) % value:
                        log.debug("fail to meet day interval condition")
                        continue
                elif key == "h":
                    if (diff / 3600) % value:
                        log.debug("fail to meet hour interval condition")
                        continue
                elif key == "m":
                    if (diff / 60) % value:
                        log.debug("fail to meet minute interval condition")
                        continue
                # execute the command
                command = " ".join(tokens[9:])
                log.info("executing command %s", command)
                exec_command(command, as_thread=options.concurrent)
            except:
                log.exception("unexpected error, see traces below")
            finally:
                log.info("--- end job %d ---", i + 1)
        log.info("<<<<<  END  >>>>>")

if __name__ == "__main__":
    utcnow = dt.datetime.now(tz.tzutc())
    log.basicConfig(format="%(asctime)s %(message)s", level=log.DEBUG)    
    try:
        main(utcnow)
    except AssertionError, ex:
        log.error(ex)
    except SystemExit:
        pass
    except:
        log.exception("unexpected error, see traces below")
