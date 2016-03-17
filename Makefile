all:
	cp -r devtools/ inspector_root/
	python devtools/scripts/CodeGeneratorFrontend.py devtools/protocol.json --output_js_dir inspector_root/front_end
