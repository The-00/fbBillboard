init_simple_config:
	rm -rf /tmp/{provider,buffer}/Folder{1,2,3} 2> /dev/null
	mkdir -p /tmp/{provider,buffer}/Folder{1,2,3}
	for s in 1 2 3; do \
		for i in 1 2 3 4 5; do \
			wget https://frog.trova.fr/api -O /tmp/provider/Folder$$s/frog_img$$i.png 2> /dev/null; \
		done; \
	done

run:
	python3 main.py --config configs_example/simple_screen_config.yaml


