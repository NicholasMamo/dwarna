NPM ?= npm

define npm-version
	$(NPM) version $(NPMFLAGS) $(1)
endef


version-major:
	$(call npm-version,major)

version-minor:
	$(call npm-version,minor)

version-patch:
	$(call npm-version,patch)


.PHONY: version-major version-minor version-patch