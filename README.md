# Cromer

Cromer is a utility that can be wrapped around any command, but is
particularly useful for wrapping around a cron job, especially to subdue
periodic failures.

Note that use is subject to the [license
conditions](https://github.com/andrewferrier/cromer/blob/master/LICENSE.txt).

It is invoked like this:

    cromer <cromer options> <the original command> <original command options>

e.g.:

    cromer -X 1d ping some.remote.host

It provides a variety of command-line options and features, and more can be
found by invoking `cromer --help`. However, the main command-line options are:

* `-X` - the original motivation for writing cromer. This can be set to any
  time period in weeks, days, hours, minutes, or seconds (e.g. `-X5w7m`).
  Assuming a command has previously run successfully, cromer will ignore
  failures within that time period by swallowing the command's return code and
  stderr, as long as the command succeeds again before the time period
  expires. State is kept by using a file of the form
  `~/.cromer.xyz123.pingsomeremotehost`, where part after the second dot is an
  MD5 hash of the complete command name (including options), and after the
  third dot is a 'compressed' readable version of the same. This option
  effectively enables cron jobs to bet set on a regular, fairly short timer
  (e.g. every hour), but occasional failures to be *ignored* - as long as the
  job generally passes. Currently there is no way to disable `-X`, but you can
  set it to a very long time period (see [this
  issue](https://github.com/andrewferrier/cromer/issues/11)).

* `-t` - very similar to the Unix command
  [timeout](http://man7.org/linux/man-pages/man1/timeout.1.html). However, the
  timeout is expressed using the same syntax as for `-X` above. Currently
  there is no way to disable `-t`, but you can set it to a very long time
  period (see [this
  issue](https://github.com/andrewferrier/cromer/issues/11)).

* `-q` - Always suppress stdout output from the command.

* `-s` - Always pipe the stdout from the command into syslog.

# Installing

You can build a Debian package by executing `make builddeb`. More information
to come later. The only non-standard Python module used in `cromer` is
`coloredlogs`, and you can build a Debian package for that by using the `make
buildprereqs` target from
[normalize-filename](https://github.com/andrewferrier/normalize-filename/blob/master/Makefile).
[This should be improved in
future](https://github.com/andrewferrier/cromer/issues/15).

# Security

At the moment, `cromer` will often put sensitive information about the command
being executed into syslog, and there is no way to disable that. This behavior
will be changed in future - see [this
bug](https://github.com/andrewferrier/cromer/issues/12).

# Hacking

`cromer` is still in early development, and I would like to make it more
robust and [add unit
tests](https://github.com/andrewferrier/cromer/issues/10). Any pull
requests/issues welcome.
