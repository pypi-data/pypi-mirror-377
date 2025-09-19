class LibTemplate < Formula
  include Language::Python::Virtualenv

  desc "Rich-powered logging helpers for colorful terminal output"
  homepage "https://github.com/bitranox/bitranox_template_py_cli"
  url "https://github.com/bitranox/bitranox_template_py_cli/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "<fill-me>"
  license "MIT"

  depends_on "python@3.10"

  resource "rich" do
    url "https://files.pythonhosted.org/packages/fe/75/af448d8e52bf1d8fa6a9d089ca6c07ff4453d86c65c145d0a300bb073b9b/rich-14.1.0.tar.gz"
    sha256 "e497a48b844b0320d45007cdebfeaeed8db2a4f4bcf49f15e455cfc4af11eaa8"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/60/6c/8ca2efa64cf75a977a0d7fac081354553ebe483345c734fb6b6515d96bbc/click-8.2.1.tar.gz"
    sha256 "27c491cc05d968d271d5a1db13e3b5a184636d9d930f148c50b038f0d0646202"
  end

  resource "lib_cli_exit_tools" do
    url "https://files.pythonhosted.org/packages/68/d6/a9d9332d5a62897a5ed16cc33ca8c8e4171559b78bd72ece6e48a5c0ffa2/lib_cli_exit_tools-1.1.0.tar.gz"
    sha256 "cbd2278a1448b6377abf571efd6921d3a9fb8f23c4a1f74734e6690beec70d4b"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/bitranox_template_py_cli --version")
  end
end
