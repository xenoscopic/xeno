#!/bin/sh


# Tests editing remote contents, as an effective test of the xeno edit, list,
# sync, and stop commands


setUp()
{
  # Stop any existing daemon
  xeno daemon --stop 

  # Stop any existing sessions
  xeno stop --all

  # Create a directory (which we can easily remove) which will contain all of
  # our testing content
  TEST_PATH="/tmp/xeno-test"
  mkdir "$TEST_PATH"

  # We override the standard xeno configuration file location so that we don't
  # clobber the user's configuration (note that this needs to be exported to
  # propagate to xeno commands)
  export XENO_CONFIGURATION_FILE="$TEST_PATH/xeno.conf"

  # Set the editor to be something harmless, which will also give us some
  # debugging inside if necessary
  xeno config core.editor "ls -lash"

  # Create some testing content
  TEST_CONTENT_PATH="$TEST_PATH/content to test"
  mkdir "$TEST_CONTENT_PATH"
  echo "Content Line 1\n\nContent Line 2\n\n" > "$TEST_CONTENT_PATH/test file"
  touch "$TEST_CONTENT_PATH/ignorable file"
  mkdir "$TEST_CONTENT_PATH/subdirectory"
  touch "$TEST_CONTENT_PATH/subdirectory/sub file"

  # Set up the expected post-sync content
  TEST_EXPECTED_PATH="$TEST_PATH/expected"
  echo "Content Line 1 (Remote)\n\nContent Line 2 (Local)\n\n" \
    > "$TEST_EXPECTED_PATH"
}


tearDown()
{
  # Remove the testing directory
  rm -rf "$TEST_PATH"

  # Unset the configuration file (needed for xeno commands to work at beginning
  # of next setUp)
  unset XENO_CONFIGURATION_FILE
}


fileEdit()
{
  # Start the editing session
  if [ "$1" = "with_ssh" ]; then
    # Use this as a poor man's approximation of launching inside an SSH session
    xeno ssh -p 22 localhost "xeno edit '$TEST_CONTENT_PATH/test file'"

    # HACK: Sleep for a few second to make sure the clone completes (since it
    # is happening in a background process)
    sleep 3
  else
    xeno edit "localhost:$TEST_CONTENT_PATH/test file"
  fi
  result=$?
  assertEquals "xeno edit should exit with code 0" 0 ${result}

  # Make sure there is a single session
  result=$(xeno list | wc -l)
  assertEquals "xeno list should return a correct session count" "1" ${result}

  # Compute the session hash
  session_id=$(ls ~/.xeno/local)

  # HACK: Sleep for a few seconds to make sure the daemon starts up.  This is
  # inherently a race condition and a crappy solution, but I don't want to loop,
  # and in any case the daemon should start up quickly.
  sleep 3

  # Make sure the daemon is running (as startd by edit)
  result=$(ps -ef -u $(id -u) \
           | grep 'xeno daemon --xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should be running" "1" ${result}

  # Stop the xeno daemon so we can sync manually
  xeno daemon --stop

  # Edit the local and remote ends
  echo "Content Line 1 (Remote)\n\nContent Line 2\n\n" \
    > "$TEST_CONTENT_PATH/test file"
  echo "Content Line 1\n\nContent Line 2 (Local)\n\n" \
    > "$HOME/.xeno/local/$session_id/test file"

  # Force a synchronization
  xeno sync --all --force
  result=$?
  assertEquals "xeno sync should exit with code 0" 0 ${result}

  # Test resultant content
  diff "$TEST_CONTENT_PATH/test file" "$TEST_EXPECTED_PATH"
  result=$?
  assertEquals "merged remote content should match" 0 ${result}

  diff "$HOME/.xeno/local/$session_id/test file" "$TEST_EXPECTED_PATH"
  result=$?
  assertEquals "merged local content should match" 0 ${result}

  # Stop the session
  xeno stop --all
  result=$?
  assertEquals "xeno stop should exit with code 0" 0 ${result}

  # Make sure there are no sessions
  result=$(xeno list | wc -l)
  assertEquals "xeno list should return a correct session count" "0" ${result}
}


testFileEdit()
{
  fileEdit "without_ssh"
}


testFileEditInSession()
{
  fileEdit "with_ssh"
}


directoryEdit()
{
  # Start the editing session
  if [ "$1" = "with_ssh" ]; then
    # Use this as a poor man's approximation of launching inside an SSH session
    xeno ssh -p 22 localhost \
      "xeno edit '$TEST_CONTENT_PATH' -i 'ignorable\ file'"

    # HACK: Sleep for a few second to make sure the clone completes (since it
    # is happening in a background process)
    sleep 3
  else
    xeno edit "localhost:$TEST_CONTENT_PATH" -i "ignorable\ file"
  fi
  result=$?
  assertEquals "xeno edit should exit with code 0" 0 ${result}

  # Make sure there is a single session
  result=$(xeno list | wc -l)
  assertEquals "xeno list should return a correct session count" "1" ${result}

  # Compute the session hash
  session_id=$(ls ~/.xeno/local)

  # Make sure that our ignore commands worked
  result=$(ls "$HOME/.xeno/local/$session_id/content to test" | wc -l)
  assertEquals "xeno should have correct file count after ignore" "2" ${result}

  # HACK: Sleep for a few seconds to make sure the daemon starts up.  This is
  # inherently a race condition and a crappy solution, but I don't want to loop,
  # and in any case the daemon should start up quickly.
  sleep 3

  # Make sure the daemon is running (as startd by edit)
  result=$(ps -ef -u $(id -u) \
           | grep 'xeno daemon --xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should be running" "1" ${result}

  # Stop the xeno daemon so we can sync manually
  xeno daemon --stop

  # Edit the local and remote ends
  echo "Content Line 1 (Remote)\n\nContent Line 2\n\n" \
    > "$TEST_CONTENT_PATH/test file"
  echo "Content Line 1\n\nContent Line 2 (Local)\n\n" \
    > "$HOME/.xeno/local/$session_id/content to test/test file"

  # Force a synchronization
  xeno sync --all --force
  result=$?
  assertEquals "xeno sync should exit with code 0" 0 ${result}

  # Test resultant content
  diff "$TEST_CONTENT_PATH/test file" "$TEST_EXPECTED_PATH"
  result=$?
  assertEquals "merged remote content should match" 0 ${result}

  diff "$HOME/.xeno/local/$session_id/content to test/test file" \
       "$TEST_EXPECTED_PATH"
  result=$?
  assertEquals "merged local content should match" 0 ${result}

  # Stop the session
  xeno stop --all
  result=$?
  assertEquals "xeno stop should exit with code 0" 0 ${result}

  # Make sure there are no sessions
  result=$(xeno list | wc -l)
  assertEquals "xeno list should return a correct session count" "0" ${result}
}


testDirectoryEdit()
{
  directoryEdit "without_ssh"
}


testDirectoryEditInSession()
{
  directoryEdit "with_ssh"
}
