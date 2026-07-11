import torch

print("Threads:", torch.get_num_threads())
print("Interop Threads:", torch.get_num_interop_threads())
