#!/bin/sh


# Tests the 'xeno fswatch' command

# @TODO(joe): a real integration test which runs fswatch and tests change detection.

testExitCodes()
{
  # Check that running with a short help flag results in a non-error exit code
  xeno fswatch -h > /dev/null 2>&1
  result=$?
  assertEquals "xeno fswatch with -h should exit with code 0" 0 ${result}

  # Check that running with a long help flag results in a non-error exit code
  xeno fswatch --help > /dev/null 2>&1
  result=$?
  assertEquals "xeno fswatch with --help should exit with code 0" 0 ${result}


  # Check that running with a short stop flag results in a non-error exit code
  xeno fswatch -s > /dev/null 2>&1
  result=$?
  assertEquals "xeno fswatch with -s should exit with code 0" 0 ${result}

  # Check that running with a long stop flag results in a non-error exit code
  xeno fswatch --stop > /dev/null 2>&1
  result=$?
  assertEquals "xeno fswatch with --stop should exit with code 0" 0 ${result}
}


testStartStop()
{
  # Kill any existing instances
  xeno fswatch --stop

  # Start an instance
  xeno fswatch
  result=$?
  assertEquals "xeno fswatch should start successfully" 0 ${result}

  # Make sure it started
  result=$(ps -U $(id -u) -o pid -o args \
           | grep 'xeno-fswatch-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno fswatch should be running" "1" ${result}

  # Stop it
  xeno fswatch --stop
  result=$?
  assertEquals "xeno fswatch should stop successfully" 0 ${result}

  # Make sure it stopped
  result=$(ps -U $(id -u) -o pid -o args \
           | grep 'xeno-fswatch-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno fswatch should not be running" "0" ${result}
}
