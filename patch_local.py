
from pathlib import Path

p = Path("DP_lora.py")
s = p.read_text(encoding="utf-8")

# 旧优化器目录未公开；
# LA-LoRA 主分支不使用这些导入。
for old in [
    "from optimizer.Nesterov import Nesterov",
    "from optimizer import LESAM, SAMS, SAMC",
]:
    assert old in s, f"Not found: {old}"
    s = s.replace(old, "# " + old)

# 降低单次评估显存需求
old = """test_dataset,
        batch_size=200,
        shuffle=False,
        num_workers=4"""

new = """test_dataset,
        batch_size=4,
        shuffle=False,
        num_workers=0"""

assert old in s
s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print("Minimal patch applied.")
