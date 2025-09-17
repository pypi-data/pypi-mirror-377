import setuptools


_ENCODING_UTF8 = "utf-8"
_MODE_R = "r"

_NEW_LINE = "\n"


def _make_descriptions():
	with open("README.md", "r", encoding="utf-8") as readme_file:
		readme_content = readme_file.read()

	title_fr = "## FRANÇAIS"
	title_en = "## ENGLISH"

	index_fr = readme_content.index(title_fr)
	index_end_fr = readme_content.index("### Dépendances")

	index_en = readme_content.index(title_en)
	index_desc_en = index_en + len(title_en)
	index_desc_end_en = readme_content.index("### Content", index_desc_en)
	index_end_en = readme_content.index("### Dependencies", index_en)

	short_description = readme_content[index_desc_en: index_desc_end_en]
	short_description = short_description.strip()
	short_description = short_description.replace(_NEW_LINE, " ")
	short_description = short_description.replace("`", "")

	long_description = readme_content[index_fr: index_end_fr]\
		+ readme_content[index_en:index_end_en].rstrip()

	return short_description, long_description


def _make_requirement_list():
	with open("requirements.txt",
			_MODE_R, encoding=_ENCODING_UTF8) as req_file:
		req_str = req_file.read()

	raw_requirements = req_str.split(_NEW_LINE)

	requirements = list()
	for requirement in raw_requirements:
		if len(requirement) > 0:
			requirements.append(requirement)

	return requirements


if __name__ == "__main__":
	short_desc, long_desc = _make_descriptions()

	setuptools.setup(
		name = "syspathmodif",
		version = "1.5.1",
		author = "Guyllaume Rousseau",
		description = short_desc,
		long_description = long_desc,
		long_description_content_type = "text/markdown",
		url = "https://github.com/GRV96/syspathmodif",
		classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python :: 3.11",
			"Topic :: Utilities"
		],
		install_requires = _make_requirement_list(),
		packages = setuptools.find_packages(
			exclude=(".github", "demos", "demo_package", "tests")),
		license = "MIT",
		license_files = ("LICENSE",))
