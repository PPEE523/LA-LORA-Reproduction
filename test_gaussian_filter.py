import ast
from pathlib import Path

import torch
import torch.nn.functional as F


# Extract the actual filter functions from DP_lora.py.
# Do not import DP_lora.py directly: importing it triggers
# argument parsing and dataset initialization.
source = Path("DP_lora.py").read_text()
tree = ast.parse(source)

names = {
    "is_lora_A_param",
    "is_lora_B_param",
    "gaussian_lowpass_1d_along_dim",
    "gaussian_lowpass_lora_grad",
}

nodes = [
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name in names
]

assert len(nodes) == len(names), "Filter functions not found"

namespace = {"torch": torch, "F": F}

module = ast.Module(body=nodes, type_ignores=[])
exec(compile(module, "DP_lora.py", "exec"), namespace)

filter_grad = namespace["gaussian_lowpass_lora_grad"]

kernel = torch.tensor([1, 4, 6, 4, 1]) / 16.0


# Test 1: A is filtered along columns (input features).
grad_A = torch.zeros(3, 9)
grad_A[1, 4] = 1.0

result_A = filter_grad(
    grad_A, "layer.lora_A.default.weight"
)

expected_A = torch.zeros_like(grad_A)
expected_A[1, 2:7] = kernel

torch.testing.assert_close(result_A, expected_A)
print("[PASS] LoRA A filter direction")


# Test 2: B is filtered along rows (output features).
grad_B = torch.zeros(9, 3)
grad_B[4, 1] = 1.0

result_B = filter_grad(
    grad_B, "layer.lora_B.default.weight"
)

expected_B = torch.zeros_like(grad_B)
expected_B[2:7, 1] = kernel

torch.testing.assert_close(result_B, expected_B)
print("[PASS] LoRA B filter direction")


# Test 3: A constant gradient remains constant.
constant = torch.ones(3, 9)

result = filter_grad(
    constant, "layer.lora_A.default.weight"
)

torch.testing.assert_close(result, constant)
print("[PASS] Constant signal preservation")


# Test 4: Classifier gradients must remain unchanged.
head_grad = torch.randn(100, 768)

result_head = filter_grad(
    head_grad, "head.weight"
)

torch.testing.assert_close(result_head, head_grad)
print("[PASS] Classifier gradient unchanged")


print("\n[SUCCESS] All Gaussian filter tests passed.")
