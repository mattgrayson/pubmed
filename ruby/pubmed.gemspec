Gem::Specification.new do |s|
  s.name = %q{pubmed}
  s.version = "0.0.1"

  s.authors = ["Matt Grayson"]
  s.date = '2010-02-02'
  s.description = %q{Simple utility for searching and retrieving articles from PubMed via the Entrez Programming Utilities <http://eutils.ncbi.nlm.nih.gov/>.}
  s.email = 'mattgrayson@eitheror.org'
  s.extra_rdoc_files = [
    "LICENSE",
    "README.rdoc"
  ]
  s.files = [
     "LICENSE",
     "README.rdoc",
     "VERSION",
     "lib/pubmed.rb",
  ]
  s.homepage = 'http://github.com/mattgrayson/pubmed'
  s.rdoc_options = ["--charset=UTF-8"]
  s.require_paths = ["lib"]
  s.rubygems_version = '1.3.5'
  s.summary = %q{Simple utility for searching and retrieving articles from PubMed via the Entrez Programming Utilities <http://eutils.ncbi.nlm.nih.gov/>.}
  s.test_files = [
    "test/helper.rb",
    "test/test_pubmed.rb"
  ]

  s.add_runtime_dependency 'nokogiri'
  s.add_runtime_dependency 'patron'
end
