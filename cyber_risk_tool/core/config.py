import yaml
import os
from utils.logger import get_logger

logger = get_logger(__name__)

def load_rules():
    rule_file = os.path.join(os.path.dirname(__file__), '..', 'rules', 'modifiers.yaml')
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
            return rules if rules is not None else {}
    except FileNotFoundError:
        logger.warning("modifiers.yaml not found, returning defaults.")
        return {}
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
        return {}
