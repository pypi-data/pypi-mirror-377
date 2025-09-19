import numpy as np
from gtda.diagrams import Amplitude
from gtda.homology import VietorisRipsPersistence

class Taelcore:
    def __init__(self,model, dataloader, num_epochs, criterion,optimizer,device=False,alpha=1e-5):
        self.model = model
        self.dataloader = dataloader
        self.num_epochs = num_epochs
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.alpha = alpha

    def transform(self):
        losses=[]
        persistence = VietorisRipsPersistence(metric = 'euclidean',homology_dimensions=[0,1,2],n_jobs=-1,collapse_edges=True)
        for epoch in range(self.num_epochs):
            epoch_loss = 0.0
            self.model.train()  # Set model to training mode
            for data, target in self.dataloader:
                if self.device:
                    data = data.to(self.device)
                    target = target.to(self.device)

                # Forward pass
                output = self.model(data)

                e = self.model.encoder(data).detach().numpy()

                dy = persistence.fit_transform(output.detach().numpy()[None,:,:])
                dz = persistence.fit_transform(e[None,:,:])
                dx = persistence.fit_transform(data[None,:,:])
                
                a1 = Amplitude(metric='bottleneck').fit_transform(dx)
                a2 = Amplitude(metric='wasserstein').fit_transform(dx)
                a3 = Amplitude(metric='landscape').fit_transform(dx)
                a4 = Amplitude(metric='betti').fit_transform(dx)
                a5 = Amplitude(metric='persistence_image').fit_transform(dx)
                
                a = a1 + a2 + a3 + a4 + a5
                
                b1 = Amplitude(metric='bottleneck').fit_transform(dz)
                b2 = Amplitude(metric='wasserstein').fit_transform(dz)
                b3 = Amplitude(metric='landscape').fit_transform(dz)
                b4 = Amplitude(metric='betti').fit_transform(dz)
                b5 = Amplitude(metric='persistence_image').fit_transform(dz)
                
                b = b1 + b2 + b3 + b4 + b5
                
                c1 = Amplitude(metric='bottleneck').fit_transform(dy)
                c2 = Amplitude(metric='wasserstein').fit_transform(dy)
                c3 = Amplitude(metric='landscape').fit_transform(dy)
                c4 = Amplitude(metric='betti').fit_transform(dy)
                c5 = Amplitude(metric='persistence_image').fit_transform(dy)
                
                c = c1 + c2 + c3 + c4 + c5
            
                
                l1 = (np.linalg.norm(a-b)**2) / 2
            
                l2 = (np.linalg.norm(b-c)**2)/2
            
                l = l1 + l2


                loss = self.criterion(output, target)+(self.alpha)*l

                # Backward pass and optimization
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                # Accumulate loss for this epoch
                # epoch_loss += loss.item() * data.size(0)
                epoch_loss += loss.data

            
            # Calculate average loss over the epoch
            epoch_loss /= len(self.dataloader.dataset)
            losses.append(epoch_loss)
            print(f'Epoch {epoch + 1}/{self.num_epochs}, Loss: {epoch_loss}')

        return self.model, losses

