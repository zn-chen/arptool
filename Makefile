DST_DIR = _build

all : $(DST_DIR) \
$(DST_DIR)/arptool-1.0.0-py3-none-any.whl

.PHONY : all

$(DST_DIR):
	mkdir -p $(DST_DIR)

$(DST_DIR)/arptool-1.0.0-py3-none-any.whl:
	python setup.py bdist_wheel
	cp dist/arptool-1.0.0-py3-none-any.whl $(DST_DIR)/arptool-1.0.0-py3-none-any.whl

clean:
	rm -rf arptool.egg-info build dist
