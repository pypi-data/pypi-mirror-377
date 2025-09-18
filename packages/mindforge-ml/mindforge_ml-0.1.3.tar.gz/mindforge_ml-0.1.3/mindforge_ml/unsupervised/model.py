import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


class AutoEncoder(nn.Module):
    def __init__(self, input_dim):
        super(AutoEncoder, self).__init__()
        self.encoder = nn.Sequential(
              nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16)
        )

        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent


# -----------------
# Unsupervised model wrapper
# -----------------

class Unsupervisedmodel:
    def __init__(self, input_dim, lr=1e-3, weight_decay=0.0, device=None):
        print("DEBUG -> weight_decay:", weight_decay)  # 👈 add this
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoEncoder(input_dim).to(self.device)
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=weight_decay)

    def fit(self, X, epochs=50, batch_size=32, verbose=True):
        dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), 
                                torch.tensor(X, dtype=torch.float32))
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.train_losses = []

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            for batch_X, _ in loader:
                batch_X = batch_X.to(self.device)
                outputs, _ = self.model(batch_X)
                loss = self.criterion(outputs, batch_X)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            
            avg_loss = total_loss / len(loader)
            self.train_losses.append(avg_loss) 
            if verbose:
                print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(loader):.4f}")

        return self.train_losses

    def transform(self, X):
        """Return latent features"""
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.inference_mode():
            _, latent = self.model(X_tensor)
        return latent.cpu().numpy()
    
    def reconstruct(self, X):
        """Reconstruct input from latent space"""
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.inference_mode():
            reconstructed, _ = self.model(X_tensor)
        return reconstructed.cpu().numpy()
    
    def anomaly_scores(self, X):
        """Return reconstruction error per sample"""
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.inference_mode():
            reconstructed, _ = self.model(X_tensor)
            errors = torch.mean((X_tensor - reconstructed) **2, dim=1)
        return errors.cpu().numpy()
    
    def save(self, path="hypertension_model.pth"):
        torch.save(self.model.state_dict(), path)

    def load(self, path="hypertension_model.pth"):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.to(self.device)



