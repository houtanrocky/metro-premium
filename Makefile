.PHONY: setup acquire acquire-osm acquire-historical audit-data prepare-data build-networks compute-accessibility analyze export-public-data report reproduce smoke test dev
setup acquire acquire-osm acquire-historical audit-data prepare-data build-networks compute-accessibility analyze export-public-data report reproduce smoke test dev:
	node scripts/task.mjs $@
