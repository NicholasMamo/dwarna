TO_COVERALLS ?= 1

ifdef TO_COVERALLS
  include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/report-cov/coveralls.mk
endif
