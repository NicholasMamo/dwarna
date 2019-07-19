# Run test suite and report code coverage.
#
# This target verifies the software's behavior by running the test suite, while
# simultaneously collecting code coverage statistics.  The test suite is
# expected to utilize Vows[^1] as a test framework.  The code itself will be
# instrumented by Istanbul[^2] in order to check code coverage.
#
# Istanbul can be installed by executing the following command:
#     $ npm install -g istanbul
#
# [^1]: http://vowsjs.org/
# [^2]: https://github.com/gotwarlost/istanbul
test-cov:
	$(ISTANBUL) cover $(ISTANBULFLAGS) --dir $(COVERAGEDIR) $(VOWS) -- $(VOWSFLAGS) $(TESTS)

# Clean up code coverage.
#
# This target cleans up any reports written while collecting code coverage
# statistics.
clean-cov:
	-rm -r $(COVERAGEDIR)


.PHONY: test-cov clean-cov