COVERALLS ?= coveralls

# Report code coverage.
#
# This target sends code coverage reports to Coveralls[^1], where they can be
# viewed and analyzed.
#
# `coveralls`[^2] can be installed by executing the following command:
#     $ npm install -g coveralls
#
# [^1]: https://coveralls.io/
# [^2]: https://github.com/nickmerwin/node-coveralls
report-cov:
	cat $(LCOVFILE) | $(COVERALLS)


.PHONY: report-cov
