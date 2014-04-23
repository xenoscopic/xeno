require 'formula'

class Xeno < Formula
  homepage 'http://xeno.io'
  url 'https://github.com/havoc-io/xeno/archive/1.0.3.tar.gz'
  version '1.0.3'
  sha1 '32fe88399a0acb915881dae000d5904575cd9585'

  def install
    bin.install 'xeno'
  end

  test do
    system "#{bin}/xeno --version | grep #{version}"
  end
end
