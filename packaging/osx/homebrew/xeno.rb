require 'formula'

class Xeno < Formula
  homepage 'http://xeno.io'
  url 'https://github.com/havoc-io/xeno/archive/1.0.2.tar.gz'
  version '1.0.2'
  sha1 'f3f7d7f2aa0aa8cb65cc11db05f30fe0680bae3f'

  def install
    bin.install 'xeno'
  end

  test do
    system "#{bin}/xeno --version | grep #{version}"
  end
end
