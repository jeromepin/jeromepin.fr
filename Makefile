HUGO_BINARY=hugo
COMMON_HUGO_PARAMS=--ignoreCache --noHTTPCache --watch

serve:
	$(HUGO_BINARY) server $(COMMON_HUGO_PARAMS)

serve-with-drafts:
	$(HUGO_BINARY) server $(COMMON_HUGO_PARAMS) --buildDrafts --buildExpired --buildFuture
