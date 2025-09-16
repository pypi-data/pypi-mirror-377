# dnn.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import numpy as np

# Neural network model
class RegressionNeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_layers, output_size, dropout_rate=0.0):
        super(RegressionNeuralNetwork, self).__init__()
        layers = []
        prev_size = input_size

        for h in hidden_layers:
            linear_layer = nn.Linear(prev_size, h)
            layers.append(linear_layer)
            layers.append(nn.ReLU())
            if dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))
            prev_size = h

        output_layer = nn.Linear(prev_size, output_size)
        layers.append(output_layer)

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

# Training function with multiple initializations
def train_regression_model(X, Y, config, num_initializations=1):
    # Dynamically get input_size and output_size
    input_size = X.shape[1]  # Number of input features
    output_size = Y.shape[1]  # Output size

    # Convert to Tensor
    X_tensor = torch.tensor(X, dtype=torch.float32)
    Y_tensor = torch.tensor(Y, dtype=torch.float32)

    # Move tensors to device only when creating DataLoader to avoid CUDA memory issues
    dataset = TensorDataset(X_tensor, Y_tensor)

    # Split dataset into training and validation sets
    val_size = int(len(dataset) * config['validation_split'])
    train_size = len(dataset) - val_size
    # Ensure reproducibility in dataset splitting
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size],
                                              generator=torch.Generator().manual_seed(config.get('seed', 0)))

    best_model_state = None
    best_val_loss_overall = float('inf')
    best_model_init = None

    for init in range(num_initializations):
        # Set different seeds for different initializations
        seed = config.get('seed', 0) + init  # Modify seed for each initialization
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        # Define the model
        model = RegressionNeuralNetwork(input_size, config['hidden_layers'], output_size, config['dropout_rate']).to(config['device'])

        # Define loss function and optimizer
        criterion = nn.MSELoss(reduction='mean')
        optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'], weight_decay=config['weight_decay'])

        # Create DataLoader for training and validation (move data to device here)
        train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=config['shuffle'])
        val_loader = DataLoader(val_dataset, batch_size=config['batch_size'])

        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state_init = None

        # Training loop
        for epoch in range(config['epochs']):
            model.train()
            total_loss = 0

            # Training step
            for X_batch, Y_batch in train_loader:
                X_batch = X_batch.to(config['device'])
                Y_batch = Y_batch.to(config['device'])
                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, Y_batch)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            # Validation step
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for X_val, Y_val in val_loader:
                    X_val = X_val.to(config['device'])
                    Y_val = Y_val.to(config['device'])
                    outputs = model(X_val)
                    loss = criterion(outputs, Y_val)
                    val_loss += loss.item()

            val_loss /= len(val_loader)
            # print(f'Initialization {init+1}, Epoch {epoch+1}, Validation Loss: {val_loss:.6f}, Training Loss: {total_loss/len(train_loader):.6f}')

            # Early stopping mechanism
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0

                # Save the best model state for this initialization
                best_model_state_init = {
                    'epoch': epoch + 1,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_loss': best_val_loss,
                }
            else:
                patience_counter += 1

            if patience_counter >= config['patience']:
                # print(f"Early stopping at epoch {epoch+1}")
                break

        # After training for this initialization, check if this is the best overall
        if best_val_loss < best_val_loss_overall:
            best_val_loss_overall = best_val_loss
            best_model_state = best_model_state_init
            best_model_init = init

    # After all initializations, load the best model state into a new model
    if best_model_state is not None:
        # Re-initialize the model with the seed corresponding to the best initialization
        seed = config.get('seed', 0) + best_model_init
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        best_model = RegressionNeuralNetwork(input_size, config['hidden_layers'], output_size, config['dropout_rate']).to(config['device'])
        best_model.load_state_dict(best_model_state['model_state_dict'])
        # Optionally, you can also return the optimizer state if needed
        # optimizer.load_state_dict(best_model_state['optimizer_state_dict'])
        # print(f"Loaded best model from initialization {best_model_init+1} with validation loss {best_val_loss_overall:.6f}")
    else:
        print("No valid model was found.")
        return None

    return best_model

    
# Classification Neural Network
class ClassificationNeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_layers, num_classes, dropout_rate=0.0):
        super(ClassificationNeuralNetwork, self).__init__()
        layers = []
        prev_size = input_size

        # Add hidden layers
        for h in hidden_layers:
            layers.append(nn.Linear(prev_size, h))
            layers.append(nn.ReLU())
            if dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))
            prev_size = h

        # Add output layer
        layers.append(nn.Linear(prev_size, num_classes))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)



# Training function for classification
def train_classification_model(X, Y, config):
    # Dynamically get input_size and num_classes
    input_size = X.shape[1]
    # Convert Y to tensor before calling torch.unique
    Y_tensor = torch.tensor(Y, dtype=torch.long).to(config['device']).view(-1)  # For classification, Y should be long tensor

    num_classes = len(torch.unique(Y_tensor))

    # Create dataset
    dataset = TensorDataset(torch.tensor(X, dtype=torch.float32).to(config['device']), Y_tensor)

    # Split dataset into training and validation sets
    val_size = int(len(dataset) * config['validation_split'])
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    # Create DataLoader for training and validation
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=config['shuffle'])
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'])

    # Define the model
    model = ClassificationNeuralNetwork(input_size, config['hidden_layers'], num_classes, config['dropout_rate']).to(config['device'])

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'], weight_decay=config['weight_decay'])

    best_val_loss = float('inf')
    patience_counter = 0

    # Training loop
    for epoch in range(config['epochs']):
        model.train()
        total_loss = 0

        # Training step
        for X_batch, Y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, Y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        # Validation step
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_val, Y_val in val_loader:
                outputs = model(X_val)
                loss = criterion(outputs, Y_val)
                val_loss += loss.item()

        val_loss /= len(val_loader)
        # print(val_loss)
        # Early stopping mechanism
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1

        if patience_counter >= config['patience']:
            break

    return model
