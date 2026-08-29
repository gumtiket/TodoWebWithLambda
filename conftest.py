import os
import sys

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-2")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))