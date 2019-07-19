PKGVERSION = $(shell node -pe "require('./package.json').version")

release-major: version-major publish

release-minor: version-minor publish

release-patch: version-patch publish

publish: publish-scm publish-npm


WITH_GIT ?= 1

ifdef WITH_GIT
  include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/release/git.mk
endif

include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/release/npm.mk


.PHONY: release-major release-minor release-patch publish