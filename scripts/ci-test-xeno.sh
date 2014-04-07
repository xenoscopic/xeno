#!/bin/sh


# Tests the 'xeno' command


testExitCodes()
{
  # Check that running without any help flag results in an error exit code
  ./xeno > /dev/null 2>&1
  result=$?
  assertEquals "xeno by itself should exit with code 1" 1 ${result}


  # Check that running with an unknown subcommand results in an error exit code
  ./xeno boguscommand > /dev/null 2>&1
  result=$?
  assertEquals "xeno with an unknown subcommand should exit with code 1" \
    1 ${result}


  # Check that running with a short version flag results in a non-error exit
  # code
  ./xeno -v > /dev/null 2>&1
  result=$?
  assertEquals "xeno with -v should exit with code 0" 0 ${result}

  # Check that running with a long version flag results in a non-error exit code
  ./xeno --version > /dev/null 2>&1
  result=$?
  assertEquals "xeno with --version should exit with code 0" 0 ${result}

  # Check that running with a short version flag with a subcommand results in a
  # non-error exit code
  ./xeno -v config > /dev/null 2>&1
  result=$?
  assertEquals "xeno with -v and a subcommand should exit with code 0" \
    0 ${result}

  # Check that running with a long version flag with a subcommand results in a
  # non-error exit code
  ./xeno --version config > /dev/null 2>&1
  result=$?
  assertEquals \
    "xeno with --version and a subcommand should exit with code 0" 0 ${result}


  # Check that running with a short help flag results in a non-error exit code
  ./xeno -h > /dev/null 2>&1
  result=$?
  assertEquals "xeno with -h should exit with code 0" 0 ${result}

  # Check that running with a long help flag results in a non-error exit code
  ./xeno --help > /dev/null 2>&1
  result=$?
  assertEquals "xeno with --help should exit with code 0" 0 ${result}

  # Check that running with a short help flag with a subcommand results in a
  # non-error exit code
  ./xeno -h config > /dev/null 2>&1
  result=$?
  assertEquals "xeno with -h and a subcommand should exit with code 0" \
    0 ${result}

  # Check that running with a long help flag with a subcommand results in a
  # non-error exit code
  ./xeno --help config > /dev/null 2>&1
  result=$?
  assertEquals "xeno with --help and a subcommand should exit with code 0" \
    0 ${result}
}
