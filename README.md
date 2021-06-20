# Cromer

**⚠️ DEPRECATED: This repository is deprecated, as I don't use cromer any more or have the time to maintain it. For now, it will remain here in case anyone wishes to fork and maintain it.**

Cromer is a utility that can be wrapped around any command, and subdues
periodic/occasional failures at calling that exact same command. It maintains
'hidden' state between invocations of the command to enable it to do this.
It is typically and particularly useful for wrapping around a cron job,
so the user isn't continually notified about commands that sometimes fail.

Note that use is subject to the [license
conditions](https://github.com/andrewferrier/cromer/blob/master/LICENSE.txt).

It is invoked like this:

    cromer <cromer options> <the original command> <original command options>

e.g.:

    cromer -X 1d ping some.remote.host

Typically, it might be used as a wrapper around a command in a cron job. Thus,
your crontab might look like this:

    */5 * * * *   cromer -X 1d -t 4m do-some-command-that-fails-from-time-to-time

In the above example, the command
`do-some-command-that-fails-from-time-to-time` will be run every 5 minutes
inside cromer by cron. Because the `-X` parameter is set to one day, this
command must successfully run and complete with no stdout/stderr output and a
zero returncode *at least* once a day for cromer not to pass through
stdout/stderr output to cron (and thus for cron to email the user or whatever
other action it would normally take). There is also a 4-minute timeout on the
command, so it will be killed (and considered by cromer to have failed) if it
doesn't complete successfully within 4 minutes.

`cromer` provides a variety of command-line options and features, and more
information can be found by invoking `cromer --help`. However, the main
command-line options are:

* `-X` - the original motivation for writing cromer. This can be set to any
  time period in weeks, days, hours, minutes, or seconds (e.g. `-X5w7m`).
  Assuming an identical command (with the same command-line parameters) has
  previously run successfully (probably by cron), cromer will ignore failures
  from invoking the exact same command again (again, probably from the same
  cron job) within that time period by swallowing the command's return code
  and stderr. If there hasn't been a success since at least the length of this
  period, and cromer is run by cron, failures will be reported as normal.
  State is kept by using a file of the form
  `~/.cromer/pingsomeremotehost.xyz123`, where the first part of the filename
  is a 'compressed' readable version of the same (this is only added when the
  `-r` option is used), and the second part is an SHA1 hash of the complete
  command name (including options). This option effectively enables cron jobs
  to be set on a regular, fairly short timer (e.g. every hour), but occasional
  failures to be *ignored* - as long as the job passes at least once every
  period specified by this option.

* `-t` - very similar to the Unix command
  [timeout](http://man7.org/linux/man-pages/man1/timeout.1.html). However, the
  timeout is expressed using the same syntax as for `-X` above.

# Pre-requisites

This is supported and tested on Python 3.3+. It is unlikely to work on an
earlier version.

# Installing

You can build a Debian package by executing `make builddeb`.

You need various Python modules installed as pre-requisites. If you aren't
installing via the Debian package, you can install these the Python way with
`pip3 install -r requirements.txt`.

`cromer` can optionally use the `coloredlogs` python module if it's present to
make syserr-based logs more attractive. There is support in my sister project
[python-deb](https://github.com/andrewferrier/python-deb) for building the
`coloredlogs` module as a Debian package.

# Hacking

Install pre-requisite packages with `pip3 install -r
requirements-hacking.txt`.

Any pull requests/issues welcome.
