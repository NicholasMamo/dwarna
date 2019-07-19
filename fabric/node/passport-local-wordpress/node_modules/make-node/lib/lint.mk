WITH_JSHINT ?= 1

ifdef WITH_JSHINT
  include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/lint/jshint.mk
endif
