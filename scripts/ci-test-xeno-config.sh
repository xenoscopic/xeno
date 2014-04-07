#!/bin/sh


# Tests the 'xeno config' command


oneTimeSetUp()
{
  # Set the XENO_CONFIGURATION_PATH environment variable so that we don't
  # pollute the user's actual configuration file
  export XENO_CONFIGURATION_FILE="/tmp/xeno.conf"
}


testExitCodes()
{
  # Check that running without any help flag results in an error exit code
  xeno config > /dev/null 2>&1
  result=$?
  assertEquals "xeno config by itself should exit with code 0" 0 ${result}


  # Check that running with a short help flag results in a non-error exit code
  xeno config -h > /dev/null 2>&1
  result=$?
  assertEquals "xeno config with -h should exit with code 0" 0 ${result}

  # Check that running with a long help flag results in a non-error exit code
  xeno config --help > /dev/null 2>&1
  result=$?
  assertEquals "xeno config with --help should exit with code 0" 0 ${result}


  # Check that running with a short clear flag results in a non-error exit code
  xeno -c > /dev/null 2>&1
  result=$?
  assertEquals "xeno config with -c should exit with code 1" 1 ${result}

  # Check that running with a long clear flag results in a non-error exit code
  xeno --clear > /dev/null 2>&1
  result=$?
  assertEquals "xeno config with --clear should exit with code 1" 1 ${result}
}


testSetRead()
{
  # Check that a value can be set and read back
  xeno config test.value "something" > /dev/null 2>&1
  result=$?
  assertEquals "xeno config should be able to set and read values" \
    $(xeno config test.value) "something"
}


testClear()
{
  # Check that a value can be set and cleared with the short clear flag
  xeno config test.value "something" > /dev/null 2>&1
  xeno config -c test.value > /dev/null 2>&1
  result=$?
  assertEquals "xeno config with -c should clear values" 0 ${result}

  # Check that a value can be set and cleared with the long clear flag
  xeno config test.value "something" > /dev/null 2>&1
  xeno config --clear test.value > /dev/null 2>&1
  result=$?
  assertEquals "xeno config with --clear should clear values" 0 ${result}
}
