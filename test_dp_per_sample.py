
import torch
from torch import nn
from dp_per_sample import dp_backward


model = nn.Linear(1, 1, bias=False)

with torch.no_grad():
    model.weight.zero_()

# Individual gradients are -20 and +18.
x = torch.tensor([[10.0], [-9.0]])
y = torch.ones(2, 1)

criterion = nn.MSELoss()

# Standard batch gradient: -1
model.zero_grad()
loss = criterion(model(x), y)
loss.backward()
batch_grad = model.weight.grad.item()

# Per-sample clipping:
# -20 -> -1
# +18 -> +1
# Clipped mean -> 0
dp_backward(
    model=model,
    inputs=x,
    targets=y,
    criterion=criterion,
    max_grad_norm=1.0,
    noise_multiplier=0.0,
)

clipped_grad = model.weight.grad.item()

print("Batch gradient:", batch_grad)
print("Per-sample clipped gradient:", clipped_grad)

assert abs(batch_grad + 1.0) < 1e-6
assert abs(clipped_grad) < 1e-6

print("[PASS] Per-sample clipping is correct.")
