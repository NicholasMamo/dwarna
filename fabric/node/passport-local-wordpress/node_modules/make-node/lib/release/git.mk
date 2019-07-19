GIT ?= git

publish-scm:
	$(GIT) push origin v$(PKGVERSION)


.PHONY: publish-scm