#!/bin/sh


# Tests the 'xeno daemon' command


testExitCodes()
{
  # Check that running with a short help flag results in a non-error exit code
  xeno daemon -h > /dev/null 2>&1
  result=$?
  assertEquals "xeno daemon with -h should exit with code 0" 0 ${result}

  # Check that running with a long help flag results in a non-error exit code
  xeno daemon --help > /dev/null 2>&1
  result=$?
  assertEquals "xeno daemon with --help should exit with code 0" 0 ${result}


  # Check that running with a short stop flag results in a non-error exit code
  xeno daemon -s > /dev/null 2>&1
  result=$?
  assertEquals "xeno daemon with -s should exit with code 0" 0 ${result}

  # Check that running with a long stop flag results in a non-error exit code
  xeno daemon --stop > /dev/null 2>&1
  result=$?
  assertEquals "xeno daemon with --stop should exit with code 0" 0 ${result}
}


testStartStop()
{
  # Kill any existing instances
  xeno daemon --stop

  # Start an instance
  xeno daemon > /dev/null 2>&1
  result=$?
  assertEquals "xeno daemon should start successfully" 0 ${result}

  # HACK: Sleep for a few seconds to make sure the daemon starts up.  This is
  # inherently a race condition and a crappy solution, but I don't want to loop,
  # and in any case the daemon should start up quickly.
  sleep 3

  # Make sure it started
  result=$(ps -ef -u $(id -u) \
           | grep 'xeno daemon --xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should be running" "1" ${result}

  # Stop it
  xeno daemon --stop > /dev/null 2>&1
  result=$?
  assertEquals "xeno daemon should stop successfully" 0 ${result}

  # Make sure it stopped
  result=$(ps -ef -u $(id -u) \
           | grep 'xeno daemon --xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should not be running" "0" ${result}
}
