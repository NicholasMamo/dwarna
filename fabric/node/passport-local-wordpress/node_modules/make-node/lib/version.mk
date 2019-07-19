WITH_NPM ?= 1

ifdef WITH_NPM
  include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/version/npm.mk
endif
