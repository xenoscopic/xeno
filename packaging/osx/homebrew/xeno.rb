require 'formula'

class Xeno < Formula
  homepage 'http://xeno.io'
  url 'https://github.com/havoc-io/xeno/archive/1.0.4.tar.gz'
  version '1.0.4'
  sha1 '1fb01583f87303eb8db03cd7ed1b34e9771dcac9'

  def install
    bin.install 'xeno'
  end

  test do
    system "#{bin}/xeno --version | grep #{version}"
  end
end
