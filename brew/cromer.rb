class Cromer < Formula
  desc "Cromer"
  homepage "http://github.com/andrewferrier/cromer"
  url "https://github.com/andrewferrier/cromer/archive/0.5.zip"
  version "0.5"

  def install
      bin.install "cromer"
      doc.install "README.md", "LICENSE.txt"
  end
end
