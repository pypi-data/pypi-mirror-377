
# tiny training script (PyTorch optional)
try:
    import torch
    x = torch.randn(32, 10)
    y = torch.randn(32, 1)
    model = torch.nn.Linear(10, 1)
    loss_fn = torch.nn.MSELoss()
    opt = torch.optim.SGD(model.parameters(), lr=0.01)
    for _ in range(2):
        opt.zero_grad(); loss = loss_fn(model(x), y); loss.backward(); opt.step()
    print("loss:", float(loss))
except Exception as e:
    print("PyTorch not installed, skipping demo:", e)
