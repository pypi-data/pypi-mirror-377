import torch

def explain_prediction(model, sample, target_class_index=None):
    """
    Compute a simple gradient-based saliency explanation for the model output
    with respect to the input features. This avoids external dependencies like SHAP.

    sample: numpy array or torch tensor of features
    returns: numpy array of saliency values with the same shape as the input sample
    """
    model.eval()
    if not isinstance(sample, torch.Tensor):
        sample = torch.tensor(sample, dtype=torch.float32)
    # Ensure batch dimension
    sample = sample.unsqueeze(0)

    # Enable gradients on the input
    sample = sample.clone().detach().requires_grad_(True)

    # Forward pass to get logits
    logits = model(sample)
    # Choose target class index; default to argmax
    if logits.ndim > 1 and logits.shape[1] > 1:
        if target_class_index is None:
            target_class_index = int(torch.argmax(logits, dim=1).item())
        target = logits[:, target_class_index].sum()
    else:
        target = logits.sum()

    # Backprop to input
    model.zero_grad(set_to_none=True)
    target.backward()

    saliency = sample.grad.detach().abs().squeeze(0)
    # Convert to numpy for downstream compatibility
    return saliency.cpu().numpy()