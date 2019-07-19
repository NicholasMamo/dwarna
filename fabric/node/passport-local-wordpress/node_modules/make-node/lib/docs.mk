WITH_MRDOC ?= 1

ifdef WITH_MRDOC
  include $(__JAREDHANSON_MAKE_NODE_DIR)/lib/docs/mr-doc.mk
endif
