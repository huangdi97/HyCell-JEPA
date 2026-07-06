.PHONY: verify verify-goal1 verify-goal2 verify-goal3 verify-goal4 verify-real-smoke train-local demo

PYTHON ?= python
STREAMLIT ?= streamlit

verify:
	$(PYTHON) -m pytest
	bash scripts/verify_goal1.sh
	bash scripts/verify_goal2.sh
	bash scripts/verify_goal3.sh
	bash scripts/verify_goal4.sh
	bash scripts/verify_goal4_real_smoke.sh

verify-goal1:
	bash scripts/verify_goal1.sh

verify-goal2:
	bash scripts/verify_goal2.sh

verify-goal3:
	bash scripts/verify_goal3.sh

verify-goal4:
	bash scripts/verify_goal4.sh

verify-real-smoke:
	bash scripts/verify_goal4_real_smoke.sh

train-local:
	$(PYTHON) scripts/train_encoder.py --config configs/train_local.yaml
	$(PYTHON) scripts/train_jepa.py --config configs/train_local.yaml

demo:
	$(STREAMLIT) run scripts/demo_app.py
