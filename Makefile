HUGO_BINARY=hugo

serve:
	$(HUGO_BINARY) server

serve-with-drafts:
	$(HUGO_BINARY) server --buildDrafts
