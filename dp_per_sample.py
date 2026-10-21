
import torch


def dp_backward(
    model,
    inputs,
    targets,
    criterion,
    max_grad_norm,
    noise_multiplier,
):
    """
    Reference per-sample clipped Gaussian gradient.

    Intended for small-batch correctness testing.
    This function alone does not establish an
    (epsilon, delta)-DP guarantee.
    """
    if max_grad_norm <= 0:
        raise ValueError("max_grad_norm must be positive")

    if noise_multiplier < 0:
        raise ValueError("noise_multiplier must be nonnegative")

    params = [
        p for p in model.parameters()
        if p.requires_grad
    ]

    if not params:
        raise ValueError("No trainable parameters")

    batch_size = inputs.shape[0]

    clipped_sums = [
        torch.zeros_like(p)
        for p in params
    ]

    loss_sum = torch.zeros((), device=inputs.device)

    for i in range(batch_size):
        model.zero_grad(set_to_none=True)

        outputs = model(inputs[i:i + 1])
        loss = criterion(
            outputs,
            targets[i:i + 1],
        )
        loss_sum += loss.detach()
        loss.backward()

        norm_sq = torch.zeros(
            (),
            device=inputs.device,
            dtype=torch.float32,
        )

        for p in params:
            if p.grad is not None:
                norm_sq += p.grad.detach().float().square().sum()

        grad_norm = norm_sq.sqrt().item()

        clip_coef = min(
            1.0,
            max_grad_norm / (grad_norm + 1e-12),
        )

        with torch.no_grad():
            for total, p in zip(clipped_sums, params):
                if p.grad is not None:
                    total.add_(
                        p.grad.detach(),
                        alpha=clip_coef,
                    )

    model.zero_grad(set_to_none=True)

    with torch.no_grad():
        for p, total in zip(params, clipped_sums):
            if noise_multiplier > 0:
                noise = torch.randn_like(total)
                total.add_(
                    noise,
                    alpha=noise_multiplier * max_grad_norm,
                )

            p.grad = total / batch_size



    return (loss_sum / batch_size).item()
