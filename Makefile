ZOLA_BINARY=zola
MANIM_BINARY=/Users/jeromepin/.asdf/installs/python/3.9.7/bin/manim

current_dir = $(shell pwd)

build:
	$(ZOLA_BINARY) build

serve:
	$(ZOLA_BINARY) serve --drafts

elasticsearch-comment-fonctionne-la-recherche-distribuee:
	$(MANIM_BINARY) render scenes/elasticsearch-comment-fonctionne-la-recherche-distribuee/elasticsearch_search_query_animation.py QueryPhase --preview --quality h --output_file=$(current_dir)/static/videos/elasticsearch-comment-fonctionne-la-recherche-distribuee/elasticsearch_search_query_animation.mp4