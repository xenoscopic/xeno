#!/bin/sh


# Tests editing a remote file, as an effective test of the xeno edit, list,
# sync, and stop commands


oneTimeSetUp()
{
  # Reset our testing environment
  xeno daemon --stop
  xeno stop --all
  xeno config core.editor "ls"

  # Create our "remote" path
  TEST_PATH="/tmp/test path"

  # Create out remote content
  echo "Content Line 1\n\nContent Line 2\n\n" > "$TEST_PATH"
  echo "Content Line 1 (Remote)\n\nContent Line 2 (Local)\n\n" > /tmp/expected
}


testFileEdit()
{
  # Start the editing session
  xeno edit "localhost:/tmp/test path"
  result=$?
  assertEquals "xeno edit should exit with code 0" 0 ${result}

  # Make sure there is a single session
  result=$(xeno list | wc -l)
  assertEquals "xeno list should return a correct session count" "1" ${result}

  # Make sure the daemon is running (as startd by edit)
  result=$(ps -ef -u $(id -u) \
           | grep 'xeno daemon --xeno-daemon-run' \
           | grep -v 'grep' \
           | wc -l)
  assertEquals "xeno daemon should be running" "1" ${result}

  # Stop the xeno daemon so we can sync manually
  xeno daemon --stop

  # Edit the local and remote ends
  echo "Content Line 1 (Remote)\n\nContent Line 2\n\n" > "$TEST_PATH"
  session_id=$(ls ~/.xeno/local)
  echo "Content Line 1\n\nContent Line 2 (Local)\n\n" \
    > "$HOME/.xeno/local/$session_id/test path"

  # Force a synchronization
  xeno sync --all --force
  result=$?
  assertEquals "xeno sync should exit with code 0" 0 ${result}

  # Test resultant content
  diff "$TEST_PATH" /tmp/expected
  result=$?
  assertEquals "merged remote content should match" 0 ${result}

  diff "$HOME/.xeno/local/$session_id/test path" /tmp/expected
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
