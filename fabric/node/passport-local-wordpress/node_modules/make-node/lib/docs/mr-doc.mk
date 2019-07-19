MRDOC ?= mr-doc

# Generate documentation.
#
# This target generates API documentation by processing source code for
# JSDoc[^1]-style comments.  Mr. Doc[^2] is used to generatate themeable
# HTML output.
#
# Mr. Doc can be installed by executing the following command:
#     $ npm install -g mr-doc
#
# [^1]: http://usejsdoc.org/
# [^2]: https://github.com/mr-doc/mr-doc
docs:
	$(MRDOC) $(MRDOCFLAGS) -s $(SRCDIR) -o $(DOCSDIR)

# Clean up documentation.
#
# This target cleans up any API documentation generated from source code.
clean-docs:
	-rm -r $(DOCSDIR)


.PHONY: docs clean-docs
