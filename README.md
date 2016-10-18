# Cromer

[![Travis CI Status](https://travis-ci.org/andrewferrier/cromer.svg?branch=master)](https://travis-ci.org/andrewferrier/cromer)

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
  previously run successfully, cromer will ignore failures within that time
  period by swallowing the command's return code and stderr, as long as the
  command succeeds again before the time period expires. State is kept by
  using a file of the form `~/.cromer.xyz123.pingsomeremotehost`, where the
  part after the second dot is an SHA1 hash of the complete command name
  (including options), and after the third dot is a 'compressed' readable
  version of the same (this latter part is only added when the `-r` option is
  used). This option effectively enables cron jobs to bet set on a regular,
  fairly short timer (e.g. every hour), but occasional failures to be
  *ignored* - as long as the job generally passes.

* `-t` - very similar to the Unix command
  [timeout](http://man7.org/linux/man-pages/man1/timeout.1.html). However, the
  timeout is expressed using the same syntax as for `-X` above.

# Pre-requisites

This is supported and tested on Python 3.3+. It is unlikely to work on an earlier version.

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

Any pull requests/issues welcome.
