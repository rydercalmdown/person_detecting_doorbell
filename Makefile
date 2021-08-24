STREAM_URI=rtsp://username:password@10.0.0.1/live

.PHONY: run
run:
	@echo "Starting Doorbell"
	@.env/bin/activate && export STREAM_URI=$(STREAM_URI) && cd src && python app.py

.PHONY: install
install:
	@cd scripts && bash install_pi.sh
