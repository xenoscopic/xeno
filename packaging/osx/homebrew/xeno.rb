require 'formula'

class Xeno < Formula
  homepage 'http://xeno.io'
  url 'https://github.com/havoc-io/xeno/archive/1.0.5.tar.gz'
  version '1.0.5'
  sha256 '2a04ff2d221f75e7222627222c9ed1267d2ceb4fba19ca7de504508acd484a06' 

  def install
    bin.install 'xeno'
  end

  test do
    system "#{bin}/xeno --version | grep #{version}"
  end
end
