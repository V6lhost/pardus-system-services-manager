VERSION = 1.0.0

PYTHON = python3
VENV_DIR = venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip
VENV_PYINSTALLER = $(VENV_DIR)/bin/pyinstaller
BUILD_DIR = debian/usr/share/pardus-system-services-manager
DEB_OUTPUT_DIR = output_deb
DEB_NAME = pardus-system-services-manager-$(VERSION).deb
SRC_DIR = src
UI_DIR = ui
REQS = requirements-lite.txt

.PHONY: all prepare build clean run install-deps

all: build

prepare:
	@if ! command -v dpkg > /dev/null 2>&1; then \
		echo "[-] ERR: 'dpkg' is not installed in this system."; \
		exit 1; \
	fi
	@echo "[+] dpkg installed."
	@echo "[*] Checking virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "[+] '$(VENV_DIR)' is not found, creating..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "[+] Updating pip, installing dependecies..."; \
		$(VENV_PIP) install --upgrade pip; \
		$(VENV_PIP) install -r $(REQS); \
	fi
	@if [ ! -d "$(UI_DIR)" ]; then \
		echo "[-] ERR: '$(UI_DIR)' Not found!"; \
		exit 1; \
	fi
	@echo "[+] Prepare is done."

update-control:
	@echo "[*] debian/DEBIAN/control version info is set $(VERSION)..."
	@if [ -f "debian/DEBIAN/control" ]; then \
		sed -i 's/^Version: .*/Version: $(VERSION)/' debian/DEBIAN/control; \
	else \
		echo "[-] Warning: debian/DEBIAN/control not found, skipping."; \
	fi

build: prepare update-control
	@echo "[+] Building with PyInstaller inside virtual environment..."
	$(VENV_PYINSTALLER) --onedir --noconsole \
		--add-data "$(UI_DIR)/:$(UI_DIR)/" \
		$(SRC_DIR)/main.py
		@echo "[+] PyInstaller is done. Starting .deb build..."
		mkdir $(DEB_OUTPUT_DIR)
		rm $(BUILD_DIR)/.gitkeep; \
		mv dist/main/* $(BUILD_DIR)/; \
		rmdir dist/main; \
		dpkg-deb --root-owner-group --build \
		debian $(DEB_OUTPUT_DIR)/$(DEB_NAME)
	@echo "[+] Build done! Output: $(DEB_OUTPUT_DIR)/$(DEB_NAME)"

install-deps:
	@if [ ! -d "$(VENV_DIR)" ]; then $(PYTHON) -m venv $(VENV_DIR); fi
	

run:
	@echo "[+] Running with Python inside virtual environment..."
	$(VENV_PYTHON) $(SRC_DIR)/main.py

clean:
	@echo "[-] Cleaning up..."
	rm -rf build/ dist/ *.spec __pycache__ $(SRC_DIR)/__pycache__ $(VENV_DIR) $(BUILD_DIR)/* $(DEB_OUTPUT_DIR)
	@echo "[+] Done."