import os

# XRPL Devnet URL (환경 변수로 재정의 가능)
DEVNET_URL = os.environ.get("XRPL_DEVNET_URL", "https://s.devnet.rippletest.net:51234")

# 테스트용 시드 (실제 운영에서는 안전하게 관리할 것)
SAMPLE_SEED = os.environ.get("XRPL_SAMPLE_SEED", "s████████████████████████████")
