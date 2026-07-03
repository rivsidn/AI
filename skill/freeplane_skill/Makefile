SKILL_NAME := freeplane
CODEX_HOME ?= $(HOME)/.codex
SKILLS_DIR ?= $(CODEX_HOME)/skills
INSTALL_DIR := $(SKILLS_DIR)/$(SKILL_NAME)

.PHONY: install uninstall validate

install: validate
	mkdir -p "$(SKILLS_DIR)"
	rm -rf "$(INSTALL_DIR)"
	cp -R "$(SKILL_NAME)" "$(INSTALL_DIR)"
	find "$(INSTALL_DIR)" -type d -name __pycache__ -prune -exec rm -rf {} +
	find "$(INSTALL_DIR)" -type f -name '*.pyc' -delete
	@echo "Installed $(SKILL_NAME) skill to $(INSTALL_DIR)"

uninstall:
	rm -rf "$(INSTALL_DIR)"
	@echo "Uninstalled $(SKILL_NAME) skill from $(INSTALL_DIR)"

validate:
	test -f "$(SKILL_NAME)/SKILL.md"
	python3 -m py_compile "$(SKILL_NAME)"/scripts/*.py
	python3 /home/yuchao/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$(SKILL_NAME)"
