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
  xeno daemon
  result=$?
  assertEquals "xeno daemon should start successfully" 0 ${result}

  # Make sure it started
  result=$(ps -U $(id -u) -o pid -o args \
           | grep 'xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should be running" "1" ${result}

  # Stop it
  xeno daemon --stop 
  result=$?
  assertEquals "xeno daemon should stop successfully" 0 ${result}

  # Make sure it stopped
  result=$(ps -U $(id -u) -o pid -o args \
           | grep 'xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should not be running" "0" ${result}
}
