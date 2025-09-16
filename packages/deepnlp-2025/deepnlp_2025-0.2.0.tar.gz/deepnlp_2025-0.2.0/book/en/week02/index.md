# Week 2 - Tool Learning: PyTorch and Latest Frameworks

## 1. PyTorch Basics: Tensors and Autograd

PyTorch provides **tensor** data structures and automatic differentiation (**Autograd**) functionality to simplify deep learning model implementation. Tensors are multi-dimensional arrays similar to NumPy arrays but support GPU acceleration and automatic differentiation. For example, you can create tensors with torch.tensor() and perform **tensor operations** like addition, multiplication, etc. Tensor operations provide various functions needed for scientific computation such as broadcasting, view transformation, matrix multiplication, etc.

PyTorch's **Autograd principle** is based on **computational graphs**. When tensor operations are performed, PyTorch dynamically generates **graph nodes** for operators and records functions (grad_fn) for backpropagation at each node. The generated **computation graph** is in the form of a directed acyclic graph (DAG), where leaf nodes are input tensors and root nodes are output (loss) tensors. According to the **chain rule**, when .backward() is called, differentiation is automatically calculated from the graph's root to leaf. The Autograd engine calls grad_fn defining differentiation formulas for each operation in sequence to propagate **gradients**. As a result, the value of d(Output)/d(Input) is stored in the grad attribute of input tensors.

For example, here's code that automatically calculates the derivative of a simple first-order function:

```python
import torch
# Set requires_grad=True to activate gradient tracking
x = torch.tensor(2.0, requires_grad=True)
y = 3*x**2 + 5*x + 1            # y = 3x^2 + 5x + 1
y.backward()                   # Differentiate y with respect to x (automatic backpropagation)
print(x.grad)                  # Output: tensor(17.)
```

In the above code, since y=3x²+5x+1, the derivative result is dy/dx=6x+5, and when x=2, 6\*2+5=17 is stored in x.grad. Like this, PyTorch Autograd automatically calculates derivatives following the **dynamic computation graph** without users having to calculate differentiation formulas manually. Also, thanks to the dynamic graph characteristics, complex models with **branches or loops** can flexibly construct graphs and process them at each iteration.

_Figure 1: Example of computation graph constructed by Autograd. Blue nodes are leaf tensors (inputs), and operation nodes represent backward functions of corresponding operations. When .backward() is executed, grad_fn of each node is called following this graph, and finally, derivative values with respect to loss are stored in grad of input tensors._

Furthermore, in PyTorch, model parameters can be updated using **gradient descent** with .grad values. Using Optimizer (torch.optim.SGD, etc.), parameters are updated based on gradients calculated by .backward(). At this time, it's important to initialize existing gradients to 0 with .zero_grad() before new iteration to prevent accumulation of gradient residues from previous steps. Through these procedures, neural networks are trained, and Autograd helps efficient learning by reconstructing graphs and performing backpropagation at each step. Also, if needed, you can inherit torch.autograd.Function for custom operations to implement custom backward functions, making it possible to extend the Autograd engine.

## 2. FlashAttention-3: Fast Attention Implementation

**Attention mechanism** is the core of Transformer models, but has limitations where **computational complexity** increases quadratically with input sequence length n as O(n²). For example, when sequence length increases (performing computation for all query-key pairs), computational cost and memory usage increase exponentially, causing **bottlenecks**. Especially in self-attention, n×n sized score matrices are created for each layer and go through Softmax, so for very long inputs, computation time slows down and GPU memory is heavily required, acting as practical limitations (e.g., BERT's maximum input 512 token limit). One technique that emerged to reduce such bottlenecks is **FlashAttention**, and **FlashAttention-1** proposed by Tri Dao et al. in 2022 optimized attention operations through **memory access minimization**. Specifically, instead of generating large attention matrices at once, it processes partial blocks repeatedly using **tiling techniques**, and recomputes necessary intermediate values to **reduce GPU global memory I/O**, dramatically improving time and memory usage. Later, **FlashAttention-2** improved GPU utilization by parallelizing work up to sequence dimensions and processing keys/values in block units, but even this only achieved about 35% utilization of theoretical performance on latest GPUs like **H100**. This was due to limitations like not fully utilizing the **asynchronous computation** capabilities of latest hardware.

**FlashAttention-3** is a latest technique that further boosts attention speed by utilizing new features of Hopper architecture (GPU). The core ideas are summarized in three points:

- **Warp-specialization based asynchronous execution**: Attention operations are subdivided so that some warps perform matrix multiplication (GEMM) using **Tensor Core** while other warps handle memory load/store with **Tensor Memory Accelerator (TMA)**. This enables **overlapping computation and data transfer** to utilize GPU resources without gaps. **Pipelining** (ping-pong scheduling) is implemented where one warp group calculates Softmax while another warp group performs matmul of the next block, making **entire computation flow without stopping**.

- **MatMul-Softmax interleaved parallelization**: Traditional attention applies Softmax after completing all query-key multiplications, but FlashAttention-3 performs multiplication and Softmax **interleaved in block units**. By repeating processing of small blocks and immediately calculating partial Softmax results to overlap with next operations, **waiting time is reduced**. This enables Tensor Core operations and memory access to occur simultaneously as much as possible on H100, improving GPU utilization.

- **FP8 low-precision support**: Attention operations are performed in low precision using **FP8** format supported by Hopper GPU. Processing per operation increases 2x compared to FP16, but FlashAttention-3 suppresses precision loss through **block-wise scaling and correction techniques**. According to the paper, when using FP8, it maintained accuracy with **2.6x smaller error** compared to existing FP8 attention while maximizing computational performance.

As a result of these optimizations, FlashAttention-3 achieved **1.5–2.0x speed improvement compared to existing methods on H100 GPU**. For example, in FP16 settings, it achieves effective performance reaching about **75%** of H100's theoretical maximum 740 TFLOP/s, which is nearly double improvement compared to FlashAttention-2. When using FP8, it achieves speeds approaching **1.2 PFLOP/s**. The figure below shows speed comparison results between FlashAttention-3 and existing implementations, where its superiority becomes more prominent as sequence length increases.

_Figure 2: Forward operation speed comparison of FlashAttention-3 on H100 (FP16, seq length↑). Blue line is existing FlashAttention-2, orange line is FlashAttention-3, and FlashAttention-3's performance improvement becomes more prominent as sequence length increases._

FlashAttention-3 is currently publicly available as **beta version** on GitHub and operates on H100 GPU in PyTorch 2.2+ and CUDA 12.3+ environments. For actual usage example, after installing the flash_attn library, you can call it as follows:

```python
from flash_attn.flash_attn_interface import flash_attn_func
# q, k, v: (batch, seq, head, dim) tensors, sm_scale: scaling
out = flash_attn_func(q, k, v, sm_scale=0.125, dropout_p=0.0, causal=True)
```

This function returns FlashAttention-optimized attention output for given query, key, value. PyTorch basic API also provides torch.nn.functional.scaled_dot_product_attention function from version 2.0, which can use optimization paths similar to FlashAttention internally depending on GPU environment. In summary, FlashAttention-3 is a technology that **restructures attention operations to be hardware-friendly**, greatly alleviating Transformer's speed bottlenecks, playing an important role in **context length expansion** and **training speed improvement** in latest large-scale models.

## 3. Hugging Face Transformers Practice

**Hugging Face Transformers** library is a Python toolkit that allows easy loading and utilization of various pre-trained NLP models (BERT, GPT, T5, etc.). In this section, we practice Korean document classification examples using Hugging Face. We examine **model loading**, **tokenizer usage**, and **pipeline API** utilization methods step by step.

### 3.1 Loading Pre-trained Models and Tokenizers

Hugging Face Hub has AutoModel and AutoTokenizer classes, so you can easily load pre-trained models and corresponding tokenizers just by model name. For example, here's code to load a BERT model fine-tuned for NSMC dataset often used in Korean movie review sentiment analysis (NSMC: Naver Sentiment Movie Corpus, positive/negative label data for movie reviews):

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "snoop2head/bert-base-nsmc"  # Example BERT fine-tuned for NSMC sentiment analysis
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

In the above code, the model and tokenizer at the path specified by model_name are downloaded from the internet. AutoTokenizer loads tokenizers specialized for that model (like BERT's WordPiece, etc.), and AutoModelForSequenceClassification loads BERT model weights fine-tuned for classification. With the loaded tokenizer and model, you can immediately try inference.

### 3.2 Input Encoding Using Tokenizer

To put natural language text into a model, it must be converted to a sequence of numeric indices through a **tokenizer**. The tokenizer splits sentences into units like WordPiece or SentencePiece and assigns IDs, creating input tensors that the model can understand. For example:

```python
text = "The movie was really fun!"
inputs = tokenizer(text, return_tensors='pt')
print(inputs)
```

The tokenizer splits the sentence "The movie was really fun!" into subword units and encodes each with IDs. Giving the return_tensors='pt' option returns it in PyTorch tensor form, and the output inputs is a dictionary with keys like input_ids, attention_mask, etc. The input_ids tensor is the token sequence that the model understands, and attention_mask indicates parts to ignore like padding.

### 3.3 Prediction Using Classification Pipeline

Using Hugging Face's **pipeline API**, you can perform the entire inference process combining tokenizer and model at once. For classification, it's convenient to use the "sentiment-analysis" pipeline:

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
result = classifier("This movie is really the best work.")
print(result)
```

In the above code, the classifier pipeline takes a string as input and immediately outputs sentiment analysis results. For example, if the sentence has positive content, you can get a dictionary like {'label': 'POSITIVE', 'score': 0.98} as a result. Internally, the pipeline performs a series of processes: converting input sentences to input_ids with the tokenizer, applying Softmax to the model's prediction results (logits), and selecting the label with the highest probability.

If you want to perform batch prediction on multiple sentences, you can give a list as input. Also, you can apply the same pattern to other datasets like **KorNLI** (Korean Natural Language Inference) by extending the example of Korean NSMC dataset. Using Hugging Face datasets library:

```python
from datasets import load_dataset
nsmc = load_dataset("nsmc")
print(nsmc['train'][0])
```

You can also load and examine the **NSMC dataset** like above (consisting of movie reviews and labels 0/1). With prepared datasets like this, you can batch convert them with tokenizers and then use Trainer API, etc., to fine-tune models. Detailed fine-tuning methods beyond this course's scope will be covered later, but the fact that you can easily try simple **inference practice** with just the combination of **pre-trained model + tokenizer + pipeline** is a major advantage of the Hugging Face ecosystem.

## 4. Introduction to Latest NLP Frameworks

Recently, new **NLP frameworks** that help with large language model (LLM) utilization and specialized applications are emerging one after another. In this section, we examine several rising tools among them: **DSPy**, **Haystack**, **CrewAI**. Each has different purposes and functions, but they are all tools that help developers build **powerful NLP pipelines or agent systems with minimal effort**.

### 4.1 DSPy: Declarative Prompt Programming

DSPy stands for **Declarative Self-Improving Python** and is a **declarative prompt programming** framework released by Databricks. It reduces the complexity of managing **long prompt strings** that arise when directly handling LLMs, and allows you to create AI programs with modular composition as if **writing code**. In short, it's designed with the philosophy of "don't hardcode prompts, write them **like programming**."

DSPy's core concepts are divided into three: **LM, Signature, Module**:

- **LM**: Specifies the language model to use. For example, if you set desired models like OpenAI API's GPT-4, HuggingFace's Llama2, etc. with dspy.LM(...) and dspy.configure(lm=...), then all subsequent modules generate results through this LM.

- **Signature**: Like specifying input and output types of functions, it declares the **input and output format** of prompt programs. For example, if you define signature like "question -> answer: int", DSPy automatically generates prompts in a structure that takes question(str) and outputs answer(int). Signatures describe the structure of prompts given to models and expected output forms (e.g., JSON format, etc.).

- **Module**: Encapsulates **prompt techniques** themselves for solving problems as modules. For example, simple Q&A can be expressed as dspy.Predict, complex thinking cases as dspy.ChainOfThought (chain of thought), tool-using agents as dspy.ReAct modules. Modules have logic implemented internally for how to compose prompts according to the corresponding techniques.

Users combine these three to create **AI programs**, then can optimize by automatically improving module prompts or adding few-shot examples through **Optimizer** built into DSPy. For example, you can make simple combinations like below:

```python
import dspy
# 1) LM setup (local Llama2 model example)
llm = dspy.LM('ollama/llama2', api_base='http://localhost:11434')
dspy.configure(lm=llm)
# 2) Signature declaration: question -> answer(int)
simple_sig = "question -> answer: int"
# 3) Module selection: Predict (basic Q&A)
simple_model = dspy.Predict(simple_sig)
# 4) Execute
result = simple_model(question="How many hours does it take from Seoul to Busan by KTX?")
print(result)
```

The above code creates a module called simple_model that defines the task of "output integer answers when receiving questions". Internally, DSPy generates optimal prompts matching these requirements and passes them to the LM. If the initially obtained answer is inaccurate, you can apply Optimizers like **BootstrapFewShot** to automatically add few-shot examples, or instruct continuous answer improvement with **Refine** modules. In this way, DSPy enables composition and optimization of complex LLM pipelines (e.g., **RAG** systems, multi-stage chains, agent loops, etc.) in module units.

DSPy's advantage is **improved productivity in prompt engineering**. Since LLM calls are designed within structured frameworks like code, it reduces the time people spend writing long prompt sentences manually and going through trial and error. Also, you can maintain the same module interface while switching various **models/techniques**, enabling **flexible experiments** like testing the same Chain-of-Thought module on both GPT-4 and Llama2 to compare performance. Thanks to the declarative approach, even **changing only part of the program** easily reflects in the entire LLM pipeline, making maintenance easy. Although it's still an early-stage framework, it's gaining attention for presenting the paradigm of **"handling LLMs like programming"**.

### 4.2 Haystack: Document-based Search and Reasoning

**Haystack** is an **open-source NLP framework** developed by Deepset in Germany, mainly used for building **knowledge-based question answering** systems. Haystack's strength lies in **flexible pipeline composition**. Users can easily create **end-to-end NLP systems** that return answers when questions are input by linking a series of stages from databases (document stores) to search engines, reader (Reader) or generator (Generator) models into one Pipeline. For example, **Retrieval QA** like "find answers to questions from given document sets" or Wikipedia-based chatbots can be implemented with Haystack.

Haystack's main components are as follows:

- **DocumentStore**: Literally a database for storing documents. It supports backends like In-Memory, Elasticsearch, FAISS, etc., and stores document text, metadata, embeddings, etc.

- **Retriever**: Plays the role of **searching** for relevant documents regarding user questions (Query). It's diversely implemented from traditional keyword-based methods like BM25 to **Dense Passage Retrieval** models like SBERT, DPR, etc. Retriever finds **top k** relevant documents from DocumentStore.

- **Reader** or **Generator**: Takes searched documents as input to generate final **answers**. **Reader** usually uses Extractive QA models (BERT-based, etc.) to extract correct answer spans from the documents, and **Generator** can generate answers using generative models like GPT. Both can be plugged in as nodes (Node) in Haystack.

- **Pipeline**: Structure that defines **query->response flow** by combining the above elements. There are simple ExtractiveQAPipeline that puts Retriever results into Reader, and GenerativeQAPipeline that creates answers generatively. You can also connect **Retriever + Large LM** like Retrieval-Augmented Generation, or implement multi-stage conditional flows.

Let's look at a **simple practice example** using Haystack. For example, if you want to create a QA system that answers questions using FAQ document collections:

```python
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack import Pipeline

# 1) Create document store and write documents
document_store = InMemoryDocumentStore()
docs = [{"content": "Drama **Squid Game** is a Korean survival drama...", "meta": {"source": "Wikipedia"}}]
document_store.write_documents(docs)

# 2) Configure Retriever and Reader
retriever = BM25Retriever(document_store=document_store)
reader = FARMReader(model_name_or_path="monologg/koelectra-base-v3-finetuned-korquad", use_gpu=False)

# 3) Build pipeline
pipeline = Pipeline()
pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

# 4) Execute QA
query = "Who is the director of Squid Game?"
result = pipeline.run(query=query, params={"Retriever": {"top_k": 5}, "Reader": {"top_k": 1}})
print(result['answers'][0].answer)
```

In the above code, we simply put one document in an in-memory document store and built a pipeline combining BM25-based Retriever and Electra Reader trained on Korean KorQuAD data. When you put a query in pipeline.run(), Retriever finds the top 5 documents, and Reader extracts and returns the answer from among them. As a result, you can get an answer like "Hwang Dong-hyuk".

Haystack's powerful point is that **components can be easily replaced or extended** like this. You can switch to Dense Retriever, or attach generative models like GPT-3 as Generator instead of Reader. It also supports complex reasoning scenarios by sequentially/parallelly configuring multiple nodes in the middle like multi-hop QA.

In industrial settings, there are many cases of using Haystack to configure **domain document search** + **QA** services or RAG pipelines that inject external knowledge into **chatbots**. In summary, Haystack is a **framework that ties search engines and NLP models together**, a tool that enables building powerful document-based QA systems with relatively little code.

### 4.3 CrewAI: Role-based Multi-Agent Framework

**CrewAI** is one of the recently spotlighted **AI agent** frameworks, a platform that organizes multiple LLM agents in **team (crew)** form to perform **collaborative work**. While existing frameworks like LangChain were centered on single agents or chains, CrewAI specializes in **role-based multi-agents**. For example, to solve one problem, you can divide roles like **Researcher, Analyst, Writer**, etc., and configure each agent to act autonomously with their own tools and goals while collaborating overall to produce final results.

CrewAI's concepts can be organized by main components as follows:

- **Crew (Team)**: Organization or environment of all agents. Crew objects contain multiple agents and oversee their **collaboration process**. One Crew corresponds to one agent team for achieving specific goals.

- **Agent**: Independent **autonomous AI**, each with defined **role**, **tools**, and **goals**. For example, a "literature researcher" agent uses web search tools to collect information, and a "report writer" agent writes final reports with writing tools and appropriate style. Agents can delegate work to other agents or request results when needed (like people collaborating in teams).

- **Process**: Defines **interaction rules** or **workflows** of agents within Crew. For example, you can set up flows like "Step 1: Researcher collects materials -> Step 2: Analyst summarizes -> Step 3: Writer organizes" as processes. In CrewAI, such processes are also extended with the concept of **Flow**, and agent execution can be controlled according to events or conditions.

Using CrewAI, developers can define each agent's role and tools, create and execute Crews to **automate complex tasks**. Let's look at a simple usage example. For instance, an agent team that finds materials and writes summary reports on given topics:

```python
from crewai import Crew, Agent, tool

# Agent definition: searcher and writer
searcher = Agent(name="Researcher", role="Information Collection", tools=[tool("wiki_browser")])
writer = Agent(name="Writer", role="Report Writing", tools=[tool("text_editor")])

# Create Crew and add agents
crew = Crew(agents=[searcher, writer], goal="Write a 1-page summary report on the given topic")
crew.run(task="Investigate and summarize traditional Korean food.")
```

The above example is conceptual code, but it describes the flow of assigning roles and tools (e.g., wiki browser, text editor functions) to Agents, registering them in Crew, and then executing. During execution, the Researcher agent first searches Wikipedia to gather information, then passes the results to the Writer agent. The Writer organizes the received information and writes a summary report to produce the final answer. All these processes occur automatically without human intervention, and the CrewAI framework manages **execution of each step and message exchange between agents**.

CrewAI's characteristics are **high flexibility and control**. Rather than simply running multiple agents independently, developers can design **collaboration patterns** as desired. Additionally, by finely configuring prompt rules, response formats, etc. for individual agents, **specialized AIs** can be built within teams. In practice, it can be applied to **automated customer support** (e.g., one agent understanding user intent, another agent searching FAQs, another agent generating responses) or **research assistants** (dividing roles to organize literature).

CrewAI is designed to be **compatible with LangChain and others** rather than being a completely new framework, allowing reuse of existing tool chains. However, due to the nature of multi-agent systems, **safety mechanism design** to prevent unexpected interactions or infinite loops is also important. CrewAI recommends setting **restrictions and policies** by role so agents only act within defined boundaries.

In summary, CrewAI is a framework that **systematizes collaboration of role-based autonomous agents**, helping multiple specialized LLMs perform more complex tasks through **division of labor and cooperation** instead of one giant LLM doing everything. This enables approaching multi-agent AI system development in an easy and standardized way.

## 5. Practice: BERT vs Mamba Model Comparison Experiment

Having studied the theory and tools of Transformer-based models and the latest SSM (State Space Model) architecture Mamba, let's perform a **small experiment comparing the two models directly**. The task is as follows:

- **Task**: Korean sentence **sentiment analysis** (positive/negative classification). For example, we'll classify sentences from the NSMC movie review dataset.

- **Models**: ① Transformer-based **BERT** (multilingual BERT or KoBERT, etc.), ② SSM-based **Mamba** (e.g., Mamba-130M level model).

- **Comparison Items**: Measure and compare **classification accuracy**, **inference speed**, and **GPU memory usage** of both models.

- **Environment**: Conduct under identical experimental conditions. (e.g., single RTX 3090 GPU, batch size 32, sequence length 128, etc.)

The experiment consists of **model preparation**, **inference and metric measurement**, and **result analysis** stages.

### 5.1 Model Preparation and Inference Code

First, we assume loading BERT and Mamba models fine-tuned on NSMC data through Hugging Face. (Currently, Mamba doesn't have as many fine-tuning examples as Transformers, but we assume they're prepared for this experiment.)

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
# Load BERT model (example: koBERT NSMC fine-tuned model)
bert_name = "skt/kobert-base-v1-nsmc"
tokenizer_bert = AutoTokenizer.from_pretrained(bert_name)
model_bert = AutoModelForSequenceClassification.from_pretrained(bert_name).cuda()

# Load Mamba model (example: Mamba 130M NSMC fine-tuned model)
mamba_name = "kuotient/mamba-ko-130m-nsmc"  # assumed path
tokenizer_mamba = AutoTokenizer.from_pretrained(mamba_name)
model_mamba = AutoModelForSequenceClassification.from_pretrained(mamba_name).cuda()
```

In the above code, we loaded both models into GPU memory. Next, we write a prediction function. We measure **inference speed** and **memory usage** by inputting test set batches into the model at once:

```python
import time

def evaluate_model(model, tokenizer, texts):
    # Encoding
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors='pt')
    inputs = {k:v.cuda() for k,v in inputs.items()}
    torch.cuda.synchronize()
    start = time.time()
    # Inference
    with torch.no_grad():
        outputs = model(**inputs)
    torch.cuda.synchronize()
    end = time.time()
    # Results and elapsed time
    probs = outputs.logits.softmax(dim=-1)
    preds = probs.argmax(dim=-1).cpu().numpy()
    elapsed = end - start
    return preds, elapsed

# Example data (batch of 64 sentences)
batch_texts = ["This movie was really the best."] * 64  # 64 example sentences (should be diverse in practice)
_, time_bert = evaluate_model(model_bert, tokenizer_bert, batch_texts)
_, time_mamba = evaluate_model(model_mamba, tokenizer_mamba, batch_texts)
print(f"BERT processing time: {time_bert:.4f}s, Mamba processing time: {time_mamba:.4f}s")
```

The evaluate_model function above takes a batch of 64 sentences, tokenizes them, performs model inference, and measures the elapsed time. Here, torch.cuda.synchronize() is used to accurately measure the end time of GPU operations. The output shows **batch inference time** for BERT and Mamba respectively.

Accuracy is measured through a pre-prepared **validation dataset**. We calculated accuracy by obtaining model predictions on the NSMC validation set (about 50,000 sentences) and comparing with correct answers. Additionally, GPU **memory usage** was checked using PyTorch's torch.cuda.max_memory_allocated() to see peak usage.

### 5.2 Result Comparison: Accuracy, Speed, Memory

The measurement results of the experiment are summarized below (hypothetical numerical examples):

| Model                  | Validation Accuracy | Inference Speed<sup>\*1</sup> | GPU Memory Usage<sup>\*2</sup> |
| :--------------------- | :----------------- | :---------------------------- | :----------------------------- |
| **BERT-base** (110M)   | 88.0%              | **120** samples/sec           | 800 MB                         |
| **Mamba-small** (130M) | 85.5%              | 100 samples/sec         | **600 MB**                    |

<small><sup>*1</sup>Inference speed is samples processed per second (based on batch size=64, seq length=128)</small>  
<small><sup>*2</sup>GPU memory usage is approximate peak value of model+utilization memory during inference</small>

Comparing the three metrics in a graph:

_Figure 3: Performance comparison of BERT and Mamba models. BERT slightly leads in sentiment classification accuracy and inference speed, but Mamba has superior GPU memory efficiency (dark blue: BERT, orange: Mamba)._

As can be seen from the table and figure, in terms of **classification accuracy**, BERT-base shows about 88% accuracy while Mamba (similar scale model) records about 85%, **slightly behind**. This may be because the Mamba architecture is not yet as specialized for Korean data as Transformers, or pre-training is insufficient. On the other hand, **inference speed** shows BERT being slightly faster under these experimental conditions. Since Mamba's linear time advantage is not prominent up to sequence length 128, the analysis shows that BERT, with fewer parameters and mature optimization, shows slightly higher **throughput**.

**GPU memory usage** is lower for the Mamba model. With the same batch and sequence length, BERT's memory occupancy increases due to intermediate outputs like attention matrices, while Mamba's memory requirements are relatively gentle due to **linear increase with sequence length characteristic of state space models**. In the above experiment, BERT used about 0.8GB and Mamba about 0.6GB of GPU memory. If sequence length or batch size is greatly increased, this difference can widen further (BERT's memory usage increases as O(n²), quickly reaching memory limits with large inputs, while Mamba increases as O(n), making it much more **memory efficient**).

Another major difference is **maximum processable context length**. BERT series are generally limited to **512 token input length**, but Mamba models can process **thousands to tens of thousands of tokens** by design. The actual Mamba-2.8B model supports up to 8,000 tokens, and research versions aim for over 1 million tokens. Therefore, SSM models like Mamba have great advantages in tasks requiring long document analysis.

## 6. Experiment Summary and Implications

Through the **BERT vs Mamba comparison experiment**, we examined the characteristics and pros/cons of both models. In summary, **existing BERT (Transformer)** models still show high accuracy and stable speed for medium-length inputs and are **still efficient in short input environments**. On the other hand, **Mamba (SSM)** models show potential for ultra-long context processing and **efficiency without performance degradation** as input length increases. However, at the current point, Transformer series are validated in terms of model completeness and optimization, while Mamba is in the research stage, so **Transformers have some advantage in general tasks** (e.g., accuracy comparison in this experiment).

**Which model is suitable for which situation?** First, **input sequence length** is the determining factor. For **short sentence-level tasks** (e.g., sentence classification, short-answer QA, etc.), using Transformers like BERT is advantageous in terms of implementation ease and performance. Rich pre-training and tuning techniques are accumulated, making it easy to achieve high accuracy with short inference latency. For **long context or document-level tasks** (e.g., summarizing documents of thousands of words, sentiment analysis of long texts, etc.), linear architectures like Mamba may be advantageous. This is because Mamba can efficiently process input lengths that are impossible or would consume many resources with Transformers. In fact, Mamba shows the ability to process up to **1 million tokens**, suggesting the possibility of opening the era of ultra-long context LLMs.

From an **inference speed** perspective, judgment should also be based on context length. With short inputs, the two models may have similar speeds or Transformers may be faster, but as input length increases, Transformers **slow down dramatically** as O(n²), so reports suggest that Mamba will show **up to 5x faster inference** in sufficiently long contexts. Additionally, Mamba has strengths in time series data and continuous stream processing due to the nature of state space models, and also has generality that can be widely applied to **speech and sequence data processing beyond language**.

**Service/Production Application Implications:** Currently in production environments, Transformer series (e.g., BERT, GPT) models are mature and widely used in terms of performance and tooling. Mamba is a very promising technology but **library support, community, and pre-trained model pools** are not as rich as Transformers yet. Therefore, more stability validation may be needed to immediately introduce Mamba as a replacement in industry. However, for services that have had difficulty with ultra-long context processing due to **memory capacity limits or latency issues**, introducing models like Mamba in the future could provide a breakthrough. For example, in **long legal document analysis services** or **chatbots that need to maintain long-term conversation history**, Mamba architecture has the potential to be a game changer.

Additionally, attention should be paid to future hybrid models (e.g., **Jamba: Transformer+Mamba mixed experts**) and competition with other linear sequence models. Currently, it can be viewed as **Transformer's universality vs. Mamba's specificity**, and in actual production, approaches to **mutually complementary utilization** of both methods are also considered. For example, a system that processes general conversations with Transformers and switches to Mamba mode when ultra-long context processing is needed for specific requests would be possible.

In summary, **BERT** and **Mamba** each have their strengths and different use cases. **Mature BERT series** are suitable for **short inputs/existing tasks**, while **Mamba** shows potential for **long inputs/new expansion tasks**. If research and technological development continue, it is expected that cases where SSMs like Mamba complement or replace Transformer limitations will gradually increase. When applying to actual services, current model stability, support tools, licenses, etc. should be comprehensively considered, but from a **future-oriented perspective, architectural innovation for ultra-long context and high-efficiency inference is being realized**, and this comparison experiment of the two models provides meaningful insights.

---

## References

- PyTorch Autograd Official Documentation – _"Autograd: Automatic Differentiation"_
- Tri Dao Blog – _"FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision"_
- Hugging Face Transformers Documentation & Tutorials
- Databricks DSPy Introduction – _Programming, not prompting_
- Deepset Haystack Documentation – _Flexible Open Source QA Framework_
- CrewAI Docs – _Role-based Autonomous Agent Teams_
- Mamba Architecture Paper – _Mamba: A Linear-Time State Space Model for Long-Range Sequences_
- _"Mamba Explained"_ - The Gradient
- _"Improving VTE Identification through Language Models from Radiology Reports: A Comparative Study of Mamba, Phi-3 Mini, and BERT"_
- _"FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision"_ - arXiv
- GitHub - Dao-AILab/flash-attention: Fast and memory-efficient exact attention
- _"Programming, Not Prompting: A Hands-on Guide to DSPy"_ - Medium
- DSPy Official Documentation
- Haystack - GeeksforGeeks
- _"Forget ChatGPT. CrewAI is the Future of AI Automation and Multi-Agent Systems"_ - Reddit
- Introduction - CrewAI Documentation
- _"Building a multi agent system using CrewAI"_ - Medium
