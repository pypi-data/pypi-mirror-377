# Week 3: Efficient Fine-Tuning with Modern PEFT Techniques

## Introduction: Why Parameter-Efficient Fine-Tuning?

In the previous weeks, we learned how to use PyTorch and Hugging Face to load pre-trained models and perform basic fine-tuning on NLP tasks. However, fully fine-tuning large language models (LLMs) like GPT, BERT, or LLaMA presents significant challenges:

- **Memory Requirements**: Fine-tuning a 7B parameter model requires ~28GB of GPU memory just for the model weights, plus additional memory for gradients and optimizer states
- **Computational Cost**: Updating billions of parameters is computationally expensive and time-consuming
- **Overfitting Risk**: With limited training data, full fine-tuning can lead to catastrophic forgetting of pre-trained knowledge
- **Storage Overhead**: Each fine-tuned model requires storing all parameters, making it impractical to maintain multiple task-specific models

**Parameter-Efficient Fine-Tuning (PEFT)** addresses these challenges by training only a small fraction of the model's parameters while keeping the rest frozen. This approach can reduce memory usage by 90%+ and training time by 10x while often achieving comparable or even superior performance to full fine-tuning.

### Key Benefits of PEFT

- **Memory Efficiency**: Train 65B parameter models on a single 48GB GPU (impossible with full fine-tuning)
- **Faster Training**: Fewer parameters mean faster gradient computations and convergence
- **Better Generalization**: Constrained parameter updates reduce overfitting on small datasets
- **Modularity**: Small adapter modules can be easily stored, shared, and swapped between tasks
- **No Inference Overhead**: Adapters can be merged back into base weights for deployment

In this lecture, we'll explore cutting-edge PEFT techniques that push efficiency even further: **WaveFT**, **DoRA**, **VB-LoRA**, **QR-Adaptor**, and **QLoRA**. These methods represent the state-of-the-art in efficient fine-tuning, enabling researchers and practitioners to adapt large models with minimal computational resources.

## Conceptual Overview of Modern PEFT Techniques

### **1. Recap: Low-Rank Adaptation (LoRA)**

Before exploring advanced PEFT methods, let's review LoRA (Low-Rank Adaptation), which forms the foundation for many modern techniques.

#### Core Concept

LoRA is based on the key insight that **weight updates during fine-tuning lie in a low-dimensional subspace**. Instead of updating the full weight matrix $W_0 \in \mathbb{R}^{d \times k}$, LoRA decomposes the update as:

$$\Delta W = A \times B$$

where:
- $A \in \mathbb{R}^{d \times r}$ and $B \in \mathbb{R}^{r \times k}$ are low-rank matrices
- $r \ll \min(d, k)$ is the rank (typically 4, 8, or 16)
- Only $A$ and $B$ are trainable parameters

The final weight becomes: $W = W_0 + \Delta W = W_0 + AB$

#### Key Advantages

- **Parameter Efficiency**: For a $d \times k$ weight matrix, LoRA uses only $r(d + k)$ parameters instead of $dk$
- **Memory Reduction**: Typically 0.1%-0.5% of original parameters
- **No Inference Overhead**: After training, $\Delta W$ can be merged into $W_0$
- **Modularity**: Adapters can be swapped for different tasks

#### Mathematical Example

For a 768×768 attention weight matrix with rank $r=8$:
- Full fine-tuning: 768² = 589,824 parameters
- LoRA: 8×(768+768) = 12,288 parameters (98% reduction!)

#### Limitations

LoRA's main limitation is the **"low-rank bottleneck"** - constraining updates to rank-$r$ matrices may limit expressiveness when very few parameters are available. This motivates the advanced methods we'll explore next.

### Checkpoint Questions

- Why does LoRA assume weight updates lie in a low-dimensional subspace?
- Calculate the parameter reduction for a 1024×1024 weight matrix with LoRA rank $r=16$
- What happens to inference speed when using LoRA adapters?

### **2. Wavelet Fine-Tuning (WaveFT)**

WaveFT (2025) represents a paradigm shift by fine-tuning models in the **wavelet domain** rather than the standard parameter space. This approach leverages the multi-scale representation capabilities of wavelets to achieve extreme parameter efficiency.

#### Core Concept

Instead of directly updating weight matrices, WaveFT:

1. **Transforms** the weight matrix $W_0$ into wavelet coefficients using a 2D wavelet transform
2. **Selects** a sparse subset of coefficients to make trainable (e.g., 0.01% of all coefficients)
3. **Trains** only these selected coefficients while keeping others at zero
4. **Reconstructs** the weight update $\Delta W$ via inverse wavelet transform
5. **Applies** the update: $W = W_0 + \Delta W$

#### Mathematical Formulation

For a weight matrix $W_0 \in \mathbb{R}^{d \times k}$:

1. **Forward Transform**: $C = \text{DWT}(W_0)$ where DWT is 2D Discrete Wavelet Transform
2. **Sparse Selection**: Choose subset $S$ of coefficients, mask others: $C_{\text{train}} = C \odot M$
3. **Training**: Update only $C_{\text{train}}$ via gradient descent
4. **Inverse Transform**: $\Delta W = \text{IDWT}(C_{\text{train}})$

#### Key Advantages

- **Extreme Sparsity**: Can train as few as 0.01% of weight coefficients
- **High-Rank Updates**: Unlike LoRA's low-rank constraint, WaveFT can produce full-rank updates
- **Multi-Scale Learning**: Wavelets capture both coarse and fine-grained patterns
- **No Inference Overhead**: After training, $\Delta W$ is merged into $W_0$

#### Why Wavelets Work

Wavelets decompose signals into multiple frequency components, similar to how JPEG compression works. This multi-scale representation allows the model to:
- Adjust broad, low-frequency patterns (global changes)
- Fine-tune high-frequency details (local adjustments)
- Capture hierarchical dependencies in the weight space


#### Performance Results

WaveFT has shown remarkable results in extreme low-parameter regimes:
- **Stable Diffusion**: Better subject fidelity and image diversity than LoRA with 10x fewer parameters
- **Language Models**: Competitive performance with 0.1% of LoRA's parameter count
- **Memory Efficiency**: Can train models with only thousands of parameters instead of millions

### Checkpoint Questions

- How does WaveFT differ from LoRA in terms of the mathematical structure of weight updates?
- Why might wavelet transforms be more effective than low-rank decomposition for certain types of weight patterns?
- What are the trade-offs between WaveFT's extreme sparsity and LoRA's low-rank approach?

### **3. Weight-Decomposed Low-Rank Adaptation (DoRA)**

DoRA (NVIDIA, 2024) addresses a key limitation of LoRA by explicitly separating **magnitude** and **direction** components of weight updates. This decomposition provides greater flexibility and often achieves superior performance compared to standard LoRA.

#### Core Concept

DoRA decomposes each weight matrix $W_0$ into two components:

1. **Direction**: $V = \frac{W_0}{||W_0||}$ (normalized weight matrix)
2. **Magnitude**: $m = ||W_0||$ (scalar or vector of norms)

The key insight is that these components can be updated **independently** during fine-tuning.

#### Mathematical Formulation

For a weight matrix $W_0 \in \mathbb{R}^{d \times k}$:

1. **Decomposition**: 
   - $V = \frac{W_0}{||W_0||_F}$ (Frobenius norm normalization)
   - $m = ||W_0||_F$ (magnitude scalar)

2. **Direction Update**: Apply LoRA to the direction
   - $\Delta V = AB$ where $A \in \mathbb{R}^{d \times r}$, $B \in \mathbb{R}^{r \times k}$
   - $V' = V + \Delta V$

3. **Magnitude Update**: Learn a scaling factor
   - $m' = m + \Delta m$ where $\Delta m$ is a learnable scalar

4. **Reconstruction**: $W' = m' \times \frac{V'}{||V'||_F}$

![DoRA Architecture](figs/image1.jpeg)
*Illustration of DoRA: the pre-trained weight $W_0$ is factored into a frozen direction $V$ and a learnable magnitude $m$. DoRA applies a LoRA-style low-rank update (matrices $A$, $B$ of rank $r$) to adjust the direction (yielding $V + \Delta V$) and also tunes the magnitude $m$. After training, the magnitude and new direction are multiplied to form the merged weight $W'$. Blue components are frozen, green are trainable (adapted from the DoRA paper).*

#### Key Advantages

- **Decoupled Updates**: Magnitude and direction can change independently
- **Better Expressiveness**: Captures both scaling and directional changes
- **Minimal Overhead**: Adds only a few magnitude parameters per layer
- **Drop-in Replacement**: Can be used wherever LoRA is applied

#### Why This Works

Traditional LoRA updates are constrained by the low-rank structure, which can limit the model's ability to make certain types of weight adjustments. DoRA addresses this by:

- **Magnitude Control**: Allows the model to scale weights up or down globally
- **Direction Flexibility**: Enables fine-grained directional adjustments via LoRA
- **Independent Learning**: Magnitude and direction updates don't interfere with each other

#### Performance Results

DoRA consistently outperforms LoRA across various benchmarks:

- **LLaMA-7B**: 3.7% average improvement on commonsense reasoning tasks
- **Parameter Efficiency**: Achieves better results with 25% fewer trainable parameters
- **Low-Rank Settings**: Particularly effective when LoRA rank is constrained
- **Training Dynamics**: Weight update patterns more closely resemble full fine-tuning

#### Implementation Considerations

DoRA adds minimal computational overhead:
- **Memory**: Only a few additional scalars per adapted layer
- **Training**: Slightly more complex gradient computation
- **Inference**: No overhead after merging (same as LoRA)

### Checkpoint Questions

- How does DoRA's weight decomposition differ from LoRA's low-rank approximation?
- Why might separating magnitude and direction updates lead to better performance?
- What are the computational trade-offs of using DoRA instead of LoRA?

### **4. VB-LoRA (Vector Bank LoRA)**

VB-LoRA (2023) pushes parameter efficiency to the extreme by introducing **global parameter sharing** across all layers. Instead of learning separate LoRA matrices for each layer, VB-LoRA maintains a shared "vector bank" that all layers can access.

#### Core Concept

VB-LoRA operates on the principle that different layers often need **similar types of updates**. Rather than learning independent $A$ and $B$ matrices for each layer, it:

1. **Maintains** a global vector bank $\mathcal{B} = \{v_1, v_2, ..., v_N\}$ of reusable vectors
2. **Composes** each layer's LoRA matrices from vectors selected from this bank
3. **Learns** selection weights and mixing coefficients for each layer

#### Mathematical Formulation

For layer $l$ with LoRA matrices $A_l$ and $B_l$:

1. **Vector Selection**: Choose top-$k$ vectors from bank $\mathcal{B}$
   - $S_l = \text{TopK}(\text{similarity}(A_l, \mathcal{B}), k)$

2. **Matrix Composition**: 
   - $A_l = \sum_{i \in S_l} w_{l,i} \cdot v_i \cdot U_{l,i}$
   - $B_l = \sum_{i \in S_l} w'_{l,i} \cdot v_i \cdot V_{l,i}$

3. **Parameter Sharing**: Only $w_{l,i}$, $w'_{l,i}$, $U_{l,i}$, $V_{l,i}$ are layer-specific

#### Key Advantages

- **Extreme Compression**: Can reduce adapter size by 100x compared to standard LoRA
- **Global Cooperation**: Layers can share learned patterns and representations
- **Scalable**: Parameter count doesn't grow linearly with model depth
- **Storage Efficient**: Ideal for deploying multiple task-specific adapters

#### Performance Results

VB-LoRA achieves remarkable compression without performance loss:

- **LLaMA2-13B**: 0.4% of standard LoRA parameters, better performance
- **Storage**: 300MB → 2.5MB adapter files (120x compression)
- **Multi-Task**: Can store 100+ adapters in space of one standard LoRA
- **Edge Deployment**: Enables fine-tuned models on resource-constrained devices

#### Implementation Details

The vector bank approach works through:

- **Differentiable Selection**: Top-$k$ selection is made differentiable for end-to-end training
- **Adaptive Mixing**: Each layer learns how to combine selected vectors optimally
- **Hierarchical Sharing**: Different layers can access different subsets of the bank

#### Use Cases

VB-LoRA is particularly valuable for:

- **Multi-Task Learning**: Training models for many different tasks
- **Edge Deployment**: Running fine-tuned models on mobile/embedded devices
- **Model Sharing**: Distributing task-specific adapters efficiently
- **Resource-Constrained Environments**: Where storage and memory are limited

### Checkpoint Questions

- How does VB-LoRA's parameter sharing differ from standard LoRA's per-layer approach?
- What are the trade-offs between global parameter sharing and layer-specific adaptation?
- Why might VB-LoRA be particularly useful for multi-task learning scenarios?

### **5. QR-Adaptor (Adaptive Rank and Quantization)**

QR-Adaptor (2025) represents a paradigm shift by **jointly optimizing quantization precision and adapter rank** for each layer. Unlike previous methods that treat quantization and adaptation separately, QR-Adaptor finds the optimal combination of bit-widths and LoRA ranks to maximize performance under memory constraints.

#### Core Concept

QR-Adaptor addresses the key insight that **different layers have different sensitivity** to quantization and adaptation:

- **Critical layers** (e.g., attention mechanisms) may need higher precision and larger adapters
- **Less sensitive layers** (e.g., some feed-forward components) can be heavily quantized with minimal adapters
- **Optimal allocation** of the memory budget across layers can outperform uniform approaches

#### Mathematical Formulation

For each layer $l$, QR-Adaptor optimizes:

$$\min_{\{b_l, r_l\}} \mathcal{L}_{\text{task}}(f(\{b_l, r_l\})) \quad \text{s.t.} \quad \sum_l \text{Memory}(b_l, r_l) \leq B$$

where:
- $b_l \in \{4, 8, 16\}$ is the bit-width for layer $l$
- $r_l \in \{0, 2, 4, 8, 16\}$ is the LoRA rank for layer $l$
- $B$ is the total memory budget
- $\mathcal{L}_{\text{task}}$ is the task-specific loss

#### Optimization Strategy

QR-Adaptor uses a **gradient-free search** approach:

1. **Calibration**: Evaluate different configurations on a small validation set
2. **Search**: Use evolutionary algorithms or Bayesian optimization to find optimal assignments
3. **Validation**: Test the best configuration on the full training set

#### Key Advantages

- **Layer-Wise Adaptivity**: Each layer gets optimal precision and rank allocation
- **Performance-First**: Directly optimizes for task performance, not just quantization error
- **Memory Efficient**: Achieves better results with the same memory budget
- **Automated**: No manual tuning of quantization/rank per layer

#### Performance Results

QR-Adaptor achieves remarkable improvements:

- **GSM8K**: 4.9% accuracy improvement over fixed-precision approaches
- **Memory Efficiency**: 4-bit models that outperform 16-bit full fine-tuning
- **Layer Allocation**: Critical layers get 8-bit precision, others use 4-bit
- **Rank Optimization**: Attention layers get rank-16, others use rank-4 or no adapter

#### Example Configuration

A typical QR-Adaptor configuration might look like:

- **Layer 1-6** (Embedding): 4-bit, no LoRA
- **Layer 7-12** (Attention): 8-bit, rank-16 LoRA
- **Layer 13-18** (Feed-forward): 4-bit, rank-4 LoRA
- **Layer 19-24** (Output): 8-bit, rank-8 LoRA

#### Implementation Considerations

QR-Adaptor requires:

- **Search Time**: Initial configuration search takes additional time
- **Calibration Data**: Needs representative data for configuration evaluation
- **Hardware Support**: Requires mixed-precision training capabilities

#### When to Use

QR-Adaptor is ideal for:

- **Memory-Constrained Deployment**: When every bit of performance matters
- **Production Systems**: Where optimal resource allocation is critical
- **Research**: Understanding layer-wise sensitivity to quantization
- **Automated Optimization**: When manual tuning is impractical

### Checkpoint Questions

- How does QR-Adaptor's layer-wise optimization differ from uniform quantization approaches?
- Why might different layers require different precision and rank allocations?
- What are the trade-offs between QR-Adaptor's search complexity and performance gains?

### **6. QLoRA and 4-bit NF4 Quantization**

QLoRA (Quantized LoRA) represents a breakthrough in efficient fine-tuning, enabling the training of 65B parameter models on a single 48GB GPU. The key innovation lies in combining 4-bit quantization with LoRA adapters while maintaining performance.

#### Core Concept

QLoRA follows a three-step approach:

1. **Quantize** the pre-trained model weights to 4-bit precision
2. **Freeze** the quantized weights (no gradient updates)
3. **Train** LoRA adapters at 16-bit precision with full backpropagation through quantized weights

This combination reduces memory usage by ~75% while preserving model performance.

#### NF4 Quantization: The Key Innovation

The success of QLoRA hinges on **NF4 (NormalFloat-4)**, a custom 4-bit data type optimized for neural network weights:

- **Information-Theoretically Optimal**: NF4 uses a logarithmic distribution that matches the normal distribution of neural weights
- **Superior Performance**: Achieves 27.4 vs 31.1 perplexity compared to standard 4-bit quantization
- **Efficient Representation**: Uses all 16 possible 4-bit values optimally across the weight distribution

#### Technical Innovations

**Double Quantization:**
- Quantizes both model weights (4-bit) and scaling factors (8-bit)
- Further reduces memory overhead without performance loss
- Implemented efficiently in the bitsandbytes library

**Paged Optimizers:**
- Swaps gradients and momentum to CPU memory during peaks
- Prevents out-of-memory errors on large models
- Enables training of models that wouldn't fit otherwise

#### Performance Results

QLoRA achieves remarkable results:

- **Memory Efficiency**: 75% reduction in memory usage
- **Performance Parity**: Matches full 16-bit fine-tuning on GLUE and instruction-following tasks
- **Scalability**: Enables fine-tuning of 30B-65B models on single GPUs
- **Speed**: 4-bit operations are often faster than 16-bit on modern hardware

![QLoRA Comparison](figs/image3.jpeg)
*Comparison of full fine-tuning vs LoRA vs QLoRA (conceptual). Left: Full fine-tuning updates all model weights (in 16-bit precision) and requires storing large optimizer states (32-bit per weight). Middle: LoRA fine-tuning keeps base weights 16-bit and frozen, and trains small 16-bit adapter matrices (much less to update; optimizer only for those). Right: QLoRA does the same low-rank adaptation but on a 4-bit quantized base model; gradients (green arrows) flow through the 4-bit model to the LoRA adapters. The magenta arrow indicates QLoRA's paged optimizer offloading states to CPU. This approach cuts memory by ~75% while preserving performance.*

#### Practical Implementation

```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Load model with quantization
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=quantization_config,
    device_map="auto"
)

# Apply LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.1
)

model = get_peft_model(model, lora_config)
```

#### When to Use QLoRA

QLoRA is ideal for:

- **Large Models**: 7B+ parameter models where memory is a constraint
- **Resource-Limited Environments**: Single GPU setups with limited memory
- **Research**: When you need to experiment with large models
- **Production**: When memory efficiency is critical

#### Limitations

- **Hardware Requirements**: Requires GPUs with 4-bit support
- **Setup Complexity**: More complex than standard fine-tuning
- **Library Dependencies**: Requires bitsandbytes and compatible transformers

### Checkpoint Questions

- How does NF4 quantization differ from standard 4-bit quantization approaches?
- What are the key technical innovations that make QLoRA work effectively?
- When would you choose QLoRA over standard LoRA or full fine-tuning?

---

## Practical Application: Implementing and Comparing PEFT Methods

Now that we understand the theoretical foundations, let's explore how to implement these techniques in practice. We'll focus on hands-on examples using PyTorch and Hugging Face libraries.

### **1. Basic LoRA Implementation**

Let's start with a complete LoRA implementation for Korean sentiment analysis:

```python
import torch
import torch.nn as nn
from transformers import (
    AutoModelForSequenceClassification, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import numpy as np

# Load Korean BERT model
model_name = "klue/bert-base"
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=2,
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Configure LoRA
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,                    # LoRA rank
    lora_alpha=32,          # Scaling factor
    target_modules=["query", "value", "key", "dense"],  # Target attention and FFN layers
    lora_dropout=0.1,
    bias="none"
)

# Apply LoRA to model
model = get_peft_model(model, lora_config)
print(f"Trainable parameters: {model.print_trainable_parameters()}")

# Prepare Korean sentiment data (example)
def prepare_dataset():
    texts = [
        "이 영화 정말 재밌어요!",
        "너무 지루하고 별로예요.",
        "배우들의 연기가 훌륭해요.",
        "스토리가 너무 복잡해요."
    ]
    labels = [1, 0, 1, 0]  # 1: positive, 0: negative
    
    # Tokenize
    encodings = tokenizer(
        texts, 
        truncation=True, 
        padding=True, 
        max_length=128,
        return_tensors="pt"
    )
    
    return Dataset.from_dict({
        "input_ids": encodings["input_ids"],
        "attention_mask": encodings["attention_mask"],
        "labels": torch.tensor(labels)
    })

# Training setup
training_args = TrainingArguments(
    output_dir="./lora_sentiment",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=100,
    evaluation_strategy="steps",
    eval_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=prepare_dataset(),
    tokenizer=tokenizer,
)

# Train the model
trainer.train()

# Save LoRA adapter
model.save_pretrained("./lora_adapter")
```

### **2. QLoRA Implementation**

Here's how to implement QLoRA for a larger model:

```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
import torch

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load model with quantization
model = AutoModelForCausalLM.from_pretrained(
    "beomi/KoAlpaca-7B",
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# Configure LoRA for QLoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Training with QLoRA
training_args = TrainingArguments(
    output_dir="./qlorafinetuned",
    num_train_epochs=3,
    per_device_train_batch_size=1,  # Smaller batch size due to memory constraints
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    remove_unused_columns=False,
)

# Use Trainer with QLoRA
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()
```

### **3. DoRA Implementation**

While DoRA isn't yet in the main PEFT library, here's a conceptual implementation:

```python
import torch
import torch.nn as nn
from peft import LoraConfig, get_peft_model

class DoRALayer(nn.Module):
    def __init__(self, base_layer, rank=8, alpha=32):
        super().__init__()
        self.base_layer = base_layer
        self.rank = rank
        self.alpha = alpha
        
        # LoRA matrices
        self.lora_A = nn.Linear(base_layer.in_features, rank, bias=False)
        self.lora_B = nn.Linear(rank, base_layer.out_features, bias=False)
        
        # Magnitude parameter
        self.magnitude = nn.Parameter(torch.ones(base_layer.out_features))
        
        # Initialize
        nn.init.kaiming_uniform_(self.lora_A.weight)
        nn.init.zeros_(self.lora_B.weight)
        
    def forward(self, x):
        # Get base output
        base_output = self.base_layer(x)
        
        # LoRA update
        lora_output = self.lora_B(self.lora_A(x)) * (self.alpha / self.rank)
        
        # Apply magnitude scaling
        scaled_output = (base_output + lora_output) * self.magnitude
        
        return scaled_output

# Usage example
def apply_dora_to_model(model, target_modules, rank=8, alpha=32):
    for name, module in model.named_modules():
        if any(target in name for target in target_modules):
            if isinstance(module, nn.Linear):
                # Replace with DoRA layer
                dora_layer = DoRALayer(module, rank=rank, alpha=alpha)
                # Update the model structure
                parent_name = '.'.join(name.split('.')[:-1])
                child_name = name.split('.')[-1]
                parent_module = model.get_submodule(parent_name)
                setattr(parent_module, child_name, dora_layer)
    
    return model
```

### **4. Comparison Framework**

Here's a framework to compare different PEFT methods:

```python
import time
import psutil
import torch
from typing import Dict, Any

class PEFTComparison:
    def __init__(self, model_name: str, dataset: Dataset):
        self.model_name = model_name
        self.dataset = dataset
        self.results = {}
    
    def evaluate_method(self, method_name: str, config: Dict[str, Any]):
        """Evaluate a PEFT method and record metrics"""
        
        # Load model
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, num_labels=2
        )
        
        # Apply PEFT method
        if method_name == "LoRA":
            peft_config = LoraConfig(**config)
            model = get_peft_model(model, peft_config)
        elif method_name == "DoRA":
            model = apply_dora_to_model(model, **config)
        # Add other methods...
        
        # Record metrics
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Training (simplified)
        trainer = Trainer(
            model=model,
            train_dataset=self.dataset,
            args=TrainingArguments(
                output_dir=f"./results/{method_name}",
                num_train_epochs=1,
                per_device_train_batch_size=8,
                logging_steps=10,
            )
        )
        
        trainer.train()
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Record results
        self.results[method_name] = {
            "trainable_params": sum(p.numel() for p in model.parameters() if p.requires_grad),
            "total_params": sum(p.numel() for p in model.parameters()),
            "training_time": end_time - start_time,
            "memory_usage": end_memory - start_memory,
            "config": config
        }
        
        return self.results[method_name]
    
    def compare_methods(self):
        """Compare all methods and print results"""
        print("PEFT Methods Comparison")
        print("=" * 50)
        
        for method, results in self.results.items():
            print(f"\n{method}:")
            print(f"  Trainable Parameters: {results['trainable_params']:,}")
            print(f"  Parameter Ratio: {results['trainable_params']/results['total_params']:.4f}")
            print(f"  Training Time: {results['training_time']:.2f}s")
            print(f"  Memory Usage: {results['memory_usage']:.2f}MB")

# Usage
comparison = PEFTComparison("klue/bert-base", train_dataset)

# Compare different methods
comparison.evaluate_method("LoRA", {"r": 8, "lora_alpha": 32})
comparison.evaluate_method("DoRA", {"target_modules": ["query", "value"], "rank": 8})
# Add more methods...

comparison.compare_methods()
```

### **5. Best Practices and Tips**

**Choosing the Right Method:**

- **Small datasets (< 1K examples)**: Use WaveFT or VB-LoRA for extreme efficiency
- **Medium datasets (1K-10K examples)**: Use DoRA for better performance than LoRA
- **Large datasets (> 10K examples)**: Use QLoRA for memory efficiency
- **Multiple tasks**: Use VB-LoRA for storage efficiency

**Hyperparameter Tuning:**

```python
# LoRA hyperparameters
lora_configs = [
    {"r": 4, "lora_alpha": 16},   # Minimal parameters
    {"r": 8, "lora_alpha": 32},   # Balanced
    {"r": 16, "lora_alpha": 64},  # High capacity
]

# Target modules selection
target_modules_options = [
    ["query", "value"],                    # Attention only
    ["query", "value", "key"],             # Full attention
    ["query", "value", "key", "dense"],    # Attention + FFN
]
```

**Memory Optimization:**

```python
# Enable gradient checkpointing
training_args = TrainingArguments(
    gradient_checkpointing=True,
    dataloader_pin_memory=False,
    dataloader_num_workers=0,
)

# Use mixed precision
training_args = TrainingArguments(
    fp16=True,  # or bf16=True for newer GPUs
)
```

### Checkpoint Questions

- How would you choose between LoRA and DoRA for a specific task?
- What are the key considerations when implementing QLoRA?
- How would you design an experiment to compare PEFT methods fairly?

## Summary and Future Directions

In this lecture, we've explored the cutting-edge landscape of Parameter-Efficient Fine-Tuning (PEFT) techniques. Let's summarize the key takeaways and look toward future developments.

### **Method Comparison Summary**

| Method | Parameter Efficiency | Performance | Use Case |
|--------|---------------------|-------------|----------|
| **LoRA** | 0.1-0.5% of model | Baseline | General purpose |
| **DoRA** | 0.1-0.5% of model | +3.7% over LoRA | Better performance needed |
| **WaveFT** | 0.01-0.1% of model | Competitive | Extreme efficiency |
| **VB-LoRA** | 0.01% of LoRA | Better than LoRA | Multi-task scenarios |
| **QR-Adaptor** | Variable | +4.9% over fixed | Memory-constrained |
| **QLoRA** | 75% memory reduction | Matches full FT | Large models |

### **Key Insights**

1. **Parameter Efficiency vs Performance Trade-off**: There's a clear spectrum from extreme efficiency (WaveFT) to better performance (DoRA), allowing practitioners to choose based on their constraints.

2. **Layer-Wise Optimization**: Methods like QR-Adaptor show that different layers have different sensitivity to quantization and adaptation, opening new optimization opportunities.

3. **Global Parameter Sharing**: VB-LoRA demonstrates that sharing parameters across layers can dramatically reduce storage while maintaining performance.

4. **Quantization Integration**: QLoRA proves that 4-bit quantization can be combined with PEFT without performance loss, enabling training of much larger models.

### **Choosing the Right Method**

**For Research and Experimentation:**
- Start with LoRA for baseline performance
- Use DoRA when you need better results
- Try WaveFT for extreme parameter constraints

**For Production Deployment:**
- Use QLoRA for large models (7B+ parameters)
- Consider QR-Adaptor for memory-constrained environments
- Use VB-LoRA for multi-task scenarios

**For Resource-Limited Environments:**
- WaveFT for minimal parameter budgets
- QLoRA for memory constraints
- VB-LoRA for storage limitations

### **Future Directions**

The field of PEFT is rapidly evolving. Key areas of future development include:

1. **Automated PEFT Selection**: AI-driven methods to automatically choose the best PEFT technique for a given task and constraints.

2. **Dynamic Adaptation**: Methods that can adjust their parameter efficiency during training based on task complexity.

3. **Cross-Modal PEFT**: Extending PEFT techniques to multimodal models (vision-language, audio-text).

4. **Hardware-Aware PEFT**: Techniques that are specifically optimized for different hardware configurations (mobile, edge, cloud).

5. **Federated PEFT**: Distributed fine-tuning where different clients use different PEFT methods based on their local constraints.

### **Practical Recommendations**

1. **Start Simple**: Begin with LoRA for most tasks, then explore more advanced methods as needed.

2. **Profile Your Constraints**: Understand your memory, compute, and storage limitations before choosing a method.

3. **Experiment Systematically**: Use the comparison framework provided to evaluate different methods on your specific task.

4. **Stay Updated**: The PEFT field is rapidly evolving, with new methods being published regularly.

5. **Consider the Full Pipeline**: Factor in not just training efficiency, but also deployment, storage, and inference considerations.

### **Final Thoughts**

PEFT techniques have democratized access to large language model fine-tuning, enabling researchers and practitioners to adapt powerful models with minimal computational resources. The methods we've explored represent the current state-of-the-art, but the field continues to evolve rapidly.

The key to success with PEFT is understanding the trade-offs between parameter efficiency, performance, and computational requirements. By choosing the right method for your specific use case and constraints, you can achieve remarkable results with minimal resources.

As we move forward, we can expect to see even more sophisticated PEFT techniques that push the boundaries of efficiency while maintaining or improving performance. The future of efficient fine-tuning is bright, and these techniques will continue to play a crucial role in making large language models accessible to everyone.

## References

1. **PEFT: Parameter-Efficient Fine-Tuning Methods for LLMs**
   - [Hugging Face Blog](https://huggingface.co/blog/samuellimabraz/peft-methods)

2. **Exploring Sparsity for Parameter Efficient Fine Tuning Using Wavelets**
   - [Literature Review](https://www.themoonlight.io/en/review/exploring-sparsity-for-parameter-efficient-fine-tuning-using-wavelets)
   - [arXiv:2505.12532](https://arxiv.org/abs/2505.12532)

3. **DoRA: Weight-Decomposed Low-Rank Adaptation**
   - [arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
   - [NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-dora-a-high-performing-alternative-to-lora-for-fine-tuning/)

4. **VB-LoRA: Extreme Parameter Efficient Fine-Tuning with Vector Banks**
   - [Hugging Face Documentation](https://huggingface.co/docs/peft/en/package_reference/vblora)

5. **Efficient Fine-Tuning of Quantized Models via Adaptive Rank and Bitwidth**
   - [arXiv:2505.03802](https://arxiv.org/abs/2505.03802)

6. **Making LLMs even more accessible with bitsandbytes, 4-bit quantization and QLoRA**
   - [Hugging Face Blog](https://huggingface.co/blog/4bit-transformers-bitsandbytes)
