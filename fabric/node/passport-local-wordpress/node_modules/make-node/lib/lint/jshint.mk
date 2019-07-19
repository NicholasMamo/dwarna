JSHINT ?= jshint

# Check code quality.
#
# This target checks the quality of the source code, helping to detect errors
# and potential problems.  JSHint[^1] is used as the linter.
#
# JSHint can be installed by executing the following command:
#     $ npm install -g jshint
#
# [^1]: http://jshint.com/
lint: lint-src lint-tests

lint-src:
	$(JSHINT) $(JSHINTFLAGS) $(SOURCES)

lint-tests:
	$(JSHINT) $(JSHINTFLAGS) $(TESTS)


.PHONY: lint lint-src lint-tests