WITH_ISTANBUL ?= 1

ifdef WITH_ISTANBUL
  include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/test-cov/istanbul.mk

  ifdef WITH_VOWS
    include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/test-cov/istanbul-vows.mk
  else ifdef WITH_MOCHA
    include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/test-cov/istanbul-mocha.mk
  endif
endif
