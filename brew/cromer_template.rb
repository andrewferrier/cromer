class Cromer < Formula
  desc "Cromer"
  homepage "http://github.com/andrewferrier/cromer"
  url "https://github.com/andrewferrier/cromer/archive/X.Y.zip"
  version "X.Y"

  depends_on :python3

  def install
      bin.install "cromer"
      doc.install "README.md", "LICENSE.txt"
  end

  test do
    system "make", "unittest"
  end
end
