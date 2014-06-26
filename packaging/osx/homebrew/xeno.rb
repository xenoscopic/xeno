require 'formula'

class Xeno < Formula
  homepage 'http://xeno.io'
  url 'https://github.com/havoc-io/xeno/archive/1.0.5.tar.gz'
  version '1.0.5'
  sha1 '5c5f962509b33b8ba7e4ad17af69f506cdd77256'

  def install
    bin.install 'xeno'
  end

  test do
    system "#{bin}/xeno --version | grep #{version}"
  end
end
