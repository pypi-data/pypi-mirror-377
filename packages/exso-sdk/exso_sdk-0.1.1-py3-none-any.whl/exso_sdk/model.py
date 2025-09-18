
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from .config import MODEL_PATH

class ExoplanetDataset(Dataset):
    def __init__(self, df, feature_cols, target_col=None):
        self.X = df[feature_cols].values.astype(np.float32)
        self.y = df[target_col].values.astype(np.float32) if target_col else None

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.y is not None:
            return self.X[idx], self.y[idx]
        else:
            return self.X[idx]

class SimpleNN(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_classes=3):
        super(SimpleNN, self).__init__()
        self.feature = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden_dim//2, num_classes)

    def forward(self, x):
        x = self.feature(x)
        logits = self.classifier(x)
        return logits

def build_model(input_dim, config=None):
    """
    Create model instance.
    """
    hidden_dim = config.get('hidden_dim', 64) if config else 64
    num_classes = config.get('num_classes', 3) if config else 3
    model = SimpleNN(input_dim, hidden_dim, num_classes)
    return model

def train_model(model, train_loader, val_loader, config):
    """
    Train model with checkpointing.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.get('lr', 1e-3))
    epochs = config.get('epochs', 10)
    best_val_loss = float('inf')

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device).long()
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * X_batch.size(0)
        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_val, y_val in val_loader:
                X_val, y_val = X_val.to(device), y_val.to(device).long()
                logits = model(X_val)
                loss = criterion(logits, y_val)
                val_loss += loss.item() * X_val.size(0)
        val_loss /= len(val_loader.dataset)

        print(f"Epoch {epoch+1}/{epochs} Train Loss: {train_loss:.4f} Val Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_model(model, MODEL_PATH)
            print("Saved best model")

def evaluate_model(model, data_loader):
    """
    Compute metrics and confusion matrix.
    """
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    y_true = []
    y_pred = []
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch = X_batch.to(device)
            logits = model(X_batch).cpu()
            preds = logits.argmax(dim=1).numpy()
            y_true.extend(y_batch.numpy())
            y_pred.extend(preds)
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    # Note: ROC AUC for multiclass requires probability estimates; omitted here
    auc = None
    cm = confusion_matrix(y_true, y_pred)
    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1, 'auc': auc, 'confusion_matrix': cm}

def predict(model, sample):
    """
    Predict single sample.
    sample: numpy array or torch tensor of features

    returns: (predicted_class_index, probabilities_np)
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    if not isinstance(sample, torch.Tensor):
        sample = torch.tensor(sample, dtype=torch.float32)
    sample = sample.to(device)
    with torch.no_grad():
        logits = model(sample.unsqueeze(0)).cpu()
        probs = torch.softmax(logits, dim=1).squeeze(0)
        pred_class = int(torch.argmax(probs).item())
    return pred_class, probs.numpy()

def save_model(model, path):
    """
    Save model weights.
    """
    torch.save(model.state_dict(), path)

def load_model(input_dim, path=MODEL_PATH, config=None):
    """
    Load model weights.
    """
    model = build_model(input_dim, config)
    checkpoint = torch.load(path, map_location='cpu')
    # Support both raw state_dict and checkpoint dict formats
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
    else:
        state_dict = checkpoint
    # Use strict=False to allow extra keys (e.g., scaler, features in checkpoint)
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model