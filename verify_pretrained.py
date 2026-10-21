
import torch
from model import swin_tiny_patch4_window7_224

path = "pretrained/swin_tiny_patch4_window7_224.pth"

checkpoint = torch.load(
    path,
    map_location="cpu",
    weights_only=False,
)

weights = checkpoint["model"]

model = swin_tiny_patch4_window7_224(num_classes=100)

# Save one parameter before loading to verify the change.
before = model.patch_embed.proj.weight.detach().clone()


weights = {
    k: v for k, v in weights.items()
    if not k.startswith("head.")
    and not k.endswith(".attn_mask")
}


result = model.load_state_dict(weights, strict=False)

after = model.patch_embed.proj.weight.detach()

print("Missing keys:", result.missing_keys)
print("Unexpected keys:", result.unexpected_keys)
print("Patch embedding changed:", not torch.equal(before, after))
print("Patch embedding matches:", torch.equal(
    after, weights["patch_embed.proj.weight"]
))

assert set(result.missing_keys) == {
    "head.weight", "head.bias"
}
assert not result.unexpected_keys
assert torch.equal(
    after, weights["patch_embed.proj.weight"]
)

print("[SUCCESS] Pretrained Swin-Tiny verified.")
