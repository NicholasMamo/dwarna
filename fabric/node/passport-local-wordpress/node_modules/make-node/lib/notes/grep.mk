GREP ?= grep
NOTES_PATTERN ?= 'TODO|FIXME|OPTIMIZE'

# Enumerate all annotations.
#
# This target searches through source code for comments indicating work that
# remains to be completed.  Any comments that begin with "TODO", "FIXME", or
# "OPTIMIZE" will be output, along with the filename and line number where they
# appear.
notes: notes-src notes-tests

notes-src:
	-$(GREP) -Ern $(NOTES_PATTERN) $(SOURCES)

notes-tests:
	-$(GREP) -Ern $(NOTES_PATTERN) $(TESTS)


.PHONY: notes notes-src notes-tests
