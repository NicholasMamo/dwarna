publish-npm:
	git checkout -q v$(PKGVERSION)
	npm publish
	git checkout -q master


.PHONY: publish-npm