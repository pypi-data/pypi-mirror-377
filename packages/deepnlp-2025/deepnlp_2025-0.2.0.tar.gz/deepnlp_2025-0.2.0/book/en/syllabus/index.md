# Syllabus

## Overview

In recent years, natural language processing (NLP) research has undergone a massive transformation. Large language models (LLMs) have dramatically improved the ability to generate and understand text, revolutionizing various application domains such as translation, question answering, and summarization. In 2024-2025, multimodal models like GPT-4o and Gemini 1.5 Pro that can process text, images, and audio have emerged, greatly expanding the scope of LLM applications. Particularly noteworthy is the emergence of **new architectures beyond Transformer**. For example, **Mamba**, a state space model (SSM), can process up to 1 million tokens with linear O(n) complexity and provides 5x faster inference speed than Transformer.

This course reflects these latest developments to learn **hands-on deep learning and NLP techniques**. Students first learn to use PyTorch and Hugging Face tools, then directly experience fine-tuning of Transformer-based models and **latest SSM architectures**, prompt engineering, retrieval-augmented generation (RAG), reinforcement learning from human feedback (RLHF), and agent framework implementation. Additionally, we cover **latest parameter-efficient fine-tuning techniques** (WaveFT, DoRA, VB-LoRA) and **advanced RAG architectures** (HippoRAG, GraphRAG), and finally complete a model that solves real problems by integrating learned content through team projects.

This course is designed for third-year undergraduate level and assumes completion of prerequisite course _Language Models and Natural Language Processing (131107967A)_. Through team projects, students challenge real problem-solving using **Korean corpora**, and in the final project phase, we provide opportunities to work with actual industry datasets and receive feedback from industry experts, considering **industry-academia collaboration**.

### Learning Objectives

- Understand the role and limitations of large language models in modern NLP and utilize related tools (PyTorch, Hugging Face, etc.).

- Understand the principles and trade-offs of **State Space Models** (e.g., Mamba, RWKV) along with Transformer and other latest architectures.

- Apply fine-tuning to pre-trained models or latest **parameter-efficient fine-tuning** methods like **WaveFT, DoRA, VB-LoRA**.

- Learn methods to systematically optimize prompts using **prompt engineering techniques** and **DSPy framework**.

- Understand the evolution of evaluation metrics (G-Eval, LiveCodeBench, etc.) and the importance of human evaluation, and learn latest alternatives to RLHF such as **DPO (Direct Preference Optimization)**.

- Design and implement **advanced RAG (Retrieval-Augmented Generation)** architectures like **HippoRAG, GraphRAG** and hybrid search strategies.

- Understand AI regulatory frameworks like **EU AI Act** and acquire methodologies for implementing responsible AI systems.

- Track latest research trends to discuss **advantages and disadvantages of latest technologies** such as multimodal LLMs, small language models (SLM), state space models (SSM), and mixture of experts (MoE).

- Understand the characteristics and challenges of Korean NLP and develop application capabilities through hands-on practice using **Korean corpora**.

- Strengthen collaboration and practical problem-solving capabilities through team projects and gain project experience connected to industry.

## Course Schedule

| Week | Main Topics and Keywords                                                                                                                 | Key Hands-on/Assignments                                                                           |
| :--: | :---------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
|  1   | Introduction to Generative AI, LLM Development, Latest Models (GPT-4o, Gemini 1.5 Pro, Claude 3 Opus)<br/>**Limitations of Transformer and Introduction to New Architectures** | PyTorch/Conda Environment Setup<br/>Question-Answering Demo using Hugging Face Pipeline               |
|  2   | PyTorch Basics, Hugging Face Transformers Usage<br/>**Introduction to Mamba and RWKV Architectures**                                                  | Loading Pre-trained Models (BERT) and Simple Classification Practice with **Korean Datasets**<br/>Mamba Model Demo |
|  3   | Fine-tuning Pre-trained Models: fine-tuning vs. full-training<br/>**Latest State Space Model Practice**                                           | Programming Assignment 1: **Performance Comparison Experiment between Transformer and SSM (Korean Classification Task)**             |
|  4   | **Scientific Prompt Engineering** – Various Techniques, DSPy Framework, Automatic Prompt Optimization                                                 | Hands-on Practice for Automatic Prompt Optimization using DSPy                                                  |
|  5   | **Latest Evaluation Systems** – G-Eval, LiveCodeBench, MMLU-Pro, etc. Domain-specific Benchmarks                                                           | Building LLM-based Automatic Evaluation System Practice                                                      |
|  6   | Seq2Seq Applications and **Multimodal Integration** – SmolVLM2, Qwen 2.5 Omni, Speech-Text Models                                                       | Multimodal Application Development Assignment 2                                                        |
|  7   | Large-scale Models and Few-shot Learning<br/>**Ultra-long Context Processing Technology** (1M+ tokens)                                                                | Long Context Processing Strategy Comparison Practice                                                               |
|  8   | **Next-generation PEFT** – WaveFT, DoRA, VB-LoRA, QLoRA, etc. Latest Techniques                                                                         | Performance Comparison Experiments of Various PEFT Techniques                                                          |
|  9   | **Advanced RAG Systems** – HippoRAG, GraphRAG, Hybrid Search Strategies                                                                      | Assignment 3: Building **Korean Enterprise Search System** based on GraphRAG                           |
|  10  | **Innovation in Alignment Techniques** – DPO, Constitutional AI, Process Reward Models                                                                | Comparison Practice between DPO and Existing RLHF Techniques                                                           |
|  11  | **Production Agent Systems** – CrewAI, Mirascope, Type-Safety Development                                                                | Multi-agent Orchestration Implementation                                                         |
|  12  | **AI Regulation and Responsible AI** – EU AI Act, Differential Privacy, Federated Learning                                                                  | Assignment for Designing Regulation-Compliant AI Systems                                                            |
|  13  | **Latest Research Trends** – Small Language Models (Gemma 3, Mistral NeMo), Enhanced Reasoning (Long CoT, PAL)                                               | Student Presentations of Latest Papers and Comprehensive Discussion                                                       |
|  14  | Final Project Development and MLOps                                                                                                         | Team Prototype Implementation and Feedback Sessions **(Industry Mentor Participation)**                                 |
|  15  | Final Project Presentations and Comprehensive Evaluation                                                                                                     | Team Presentations, Course Content Summary and Future Prospects Discussion                                            |

## Weekly Educational Content

### Week 1 – Understanding Next-Generation NLP Architectures

#### _Core Topics_

- **Beyond Transformer:** Recent research has seen the emergence of new architectures that overcome the $O(n^2)$ complexity limitations of Transformer. For example, **Mamba** uses selective state space models (SSM) to process sequences of up to 1 million tokens in **linear time**, and **RWKV** can process over 5 million messages per day at 10-100x lower cost than existing methods in real-time.

- **Hybrid Architectures:** Jamba (total 52B parameters) combines Transformer and Mamba with mixture of experts (MoE) to achieve both efficiency and performance. Along with this, Transformer variants utilizing **linear approaches** (GLA, Sparse-K Attention, etc.) are also gaining attention.

- **Rise of Open Source Models:** Multiple open source LLMs such as Llama 3(405B), Mixtral 8×7B, Qwen2-72B are achieving performance close to GPT-4, accelerating industrial adoption.

#### _Hands-on/Activities_

- **Environment Setup:** Conda virtual environment configuration, PyTorch and Hugging Face Transformers installation, **Mamba library** installation
- **Demo:** Comparative experiment of **inference speed** between Transformer-based models and Mamba models for the same question-answering task

### Week 2 – Tool Learning: PyTorch and Latest Frameworks

- **Framework Basics:** PyTorch tensor operations and automatic differentiation basics, latest **FlashAttention-3** utilization (1.5-2× speed improvement on H100 GPU)
- **Ecosystem Tools:** Hugging Face Transformers practice and introduction to specialized NLP frameworks like **DSPy**, **Haystack**, **CrewAI**
- **Practice:** Load BERT and Mamba models respectively to compare performance and efficiency in **identical Korean text classification tasks**

### Week 3 – Latest Techniques for Efficient Fine-tuning

- **Next-generation PEFT Methodologies:** Concepts and implementation of latest parameter-efficient fine-tuning techniques

  - **WaveFT:** Improves efficiency by sparsifying parameter updates in frequency (wavelet) domain
  - **DoRA:** Adaptive fine-tuning through weight decomposition
  - **VB-LoRA:** Vector bank-based LoRA extension for multi-user/task environments
  - **QR-Adaptor:** Adapter technique that simultaneously optimizes quantization bitwidth and LoRA rank

- **Evolution of Quantization:** 4-bit quantization format **NF4 (NormalFloat4)** has become the standard for QLoRA, enabling 7B models to be reduced from ~10GB to ~1.5GB memory
- **Assignment 1:** Performance comparison experiment of LoRA, DoRA, WaveFT on identical **Korean datasets** to analyze fine-tuning efficiency and performance retention rate

### Week 4 – Scientific Prompt Engineering

- **Systematic Prompt Techniques:** Learning various prompt technique cases (e.g., role assignment, systematic questioning, etc.)
- **Advanced Core Techniques:** Major prompt techniques that led to performance improvements

  - _Self-Consistency:_ Multiple solution path exploration in math problem solving achieving **17%p** improvement on GSM8K benchmark
  - _Tree of Thoughts:_ Expanding branches of thought in problem solving achieving **74%** success rate in Game of 24 (vs. previous 9%)
  - _DSPy Framework:_ Paradigm of "programming prompts like code" to automatically generate/combine optimal prompts

- **Automatic Prompt Optimization:** Introduction of cases like achieving **93%** accuracy on GSM8K through APE (Automatic Prompt Engineering) technique
- **Practice:** Build **automatic prompt optimization pipeline** for given problems using DSPy and compare results with existing techniques

### Week 5 – Next-Generation Evaluation Systems

- **Paradigm Shift in Evaluation:** Transition from traditional answer matching evaluation to meta-evaluation using LLMs

  - _G-Eval:_ GPT-4-based LLM uses chain-of-thought to evaluate response quality of other LLMs
  - _LiveCodeBench:_ **Contamination-free** code evaluation adopting online coding contest methods
  - _MMLU-Pro:_ Multi-turn knowledge evaluation set requiring multi-step reasoning with choices increased from 4→10

- **Domain-specific Benchmarks:** Specialized benchmarks like FinBen (36 financial task sets) for financial domain, AgentHarm (110 malicious agent scenarios) for agent risk assessment
- **Practice:** Apply G-Eval and existing automatic evaluation metrics (BLEU, ROUGE, etc.) to identical responses and compare analysis results

### Week 6 – Innovation in Multimodal NLP

- **"Any-to-Any" Model Emergence:** Development of universal input/output processing models

  - _SmolVLM2 (256M–2.2B):_ Lightweight vision-language model performing **video understanding** with small parameters
  - _Qwen 2.5 Omni:_ Integrated multimodal architecture enabling mutual conversion between text-image-speech
  - _QVQ-72B (Preview):_ First open-source large multimodal reasoning model (text→vision→query form conversion)

- **Advancement in Speech Integration:** Integrating real-time speech processing with LLM

  - _Voxtral:_ Open-source speech recognition model with performance exceeding Whisper
  - _Orpheus:_ TTS model that clones and synthesizes speaker's voice in zero-shot

- **Assignment 2:** Develop multimodal QA application responding to **mixed queries** of image-text-speech input (e.g., asking questions with voice and generating answers with image and text)

### Week 7 – Long Context Processing and Efficient Inference

- **Extreme Context Extension:** Emergence of ultra-long context supporting LLMs

  - _Gemini 1.5 Pro:_ Large multimodal model capable of processing up to **1 million tokens** (research version targeting 10 million tokens)
  - _Magic LTM-2-Mini:_ Implementing **100 million token** context window with economical structure (1/1000 cost level compared to Llama at same performance)

- **Efficient Long Context Mechanisms:** Analysis of ultra-long context implementation techniques like Flash Linear Attention, LongRoPE (long context positional encoding)
- **Practice:** Implement **RAG (Retrieval-Augmented Generation)** based summarization system for long context conversation scenarios and compare performance with ultra-long context LLMs

### Week 8 – Advanced PEFT Techniques

- **Achieving 95% Performance with Lightweight Fine-tuning:** Latest methods that change <1% parameters without performance degradation compared to full fine-tuning
- **Comparison of Major Techniques:** Comparison of actual implementation difficulty and effectiveness of each PEFT method

  - Memory usage (storage space) comparison
  - Inference speed and latency benchmarks
  - Evaluation of multi-task adaptation possibility with single prompt

- **Practice:** Conduct fine-tuning experiments with various PEFT methods for given NLP tasks and write PEFT selection guide considering utilization in **production environments**

### Week 9 – Advanced RAG Architectures

- **Next-generation RAG Systems:** New techniques for large-scale knowledge integration

  - _HippoRAG:_ Adopting human memory (Hippocampus) mechanism to **reduce vector DB storage space by 25%** and improve long-term memory
  - _GraphRAG:_ Modeling inter-context associations using knowledge graphs, improving query response precision to **99%**
  - Hybrid Search: Multi-factor search combining latest dense embeddings (NV-Embed-v2) with sparse methods (SPLADE) and graph exploration

- **Production Cases:** Analysis of large-scale RAG system structure achieving **P95 response latency <100ms** while processing over 10 million input tokens daily
- **Assignment 3:** Build **Korean enterprise search** system based on GraphRAG and apply to in-house knowledge base question answering

### Week 10 – Innovation in Alignment Techniques

- **Beyond RLHF:** New approaches to improve usefulness and safety of LLM outputs

  - _DPO (Direct Preference Optimization):_ User preference learning without separate reward models (simplified compared to RLHF)
  - _Constitutional AI:_ AI self-corrects responses according to over 75 constitutional principles to suppress harmful content generation
  - _Process Supervision:_ Reward model technique giving granular feedback on **process (Chain-of-Thought)** rather than final answers
  - _RLAIF (RL from AI Feedback):_ Utilizing AI evaluators instead of humans to mimic human-level response quality

- **Open Source Implementation Trends:** Introduction of public implementations like TRL (Transformer Reinforcement Learning) library, OpenRLHF project (3-4× speed improvement compared to existing DeepSpeed-Chat)
- **Practice:** Compare responses of models fine-tuned with DPO and RLHF for identical control instructions

### Week 11 – Production Agent Systems

- **Specialized Agent Frameworks:** Introduction of agent development tools utilized in actual services

  - _CrewAI:_ Role-based multi-agent collaboration scenario building framework (e.g., assigning roles to multiple GPT instances to work like a team)
  - _Mirascope:_ Agent development tool improving **type safety** of prompt input/output with Pydantic data validation
  - _Haystack:_ Open-source framework specialized for document RAG pipelines (easy customization of search-comprehension chains)

- **Low-code Integration Platforms:** Utilization of tools like Flowise AI, n8n, Langflow that can design prompts and workflows through GUI
- **Practice:** Implement **automated customer service system** using multi-agent frameworks (e.g., FAQ answering, database query, issue ticket generation agent linkage)

### Week 12 – AI Regulation and Responsible AI

- **EU AI Act (Effective August 2024):** Analysis of main contents of world's first comprehensive AI legislation and impact on developers/service providers
- **Privacy Enhancement Technologies:** Techniques for protecting personal and sensitive information required for generative AI services

  - Introducing **differential privacy** to text embeddings to prevent user data exposure
  - Utilizing **federated learning** for collaborative learning without central servers
  - **Homomorphic encryption** technology utilizing encrypted data for model training

- **Industry-specific Regulation Compliance:** Design of NLP solutions tailored to **domain-specific regulations** like HIPAA for healthcare, GDPR/Basel for finance, FERPA for education
- **Assignment:** Design **suitable LLM service** for given scenarios according to EU AI Act standards and create regulatory compliance checklist

### Week 13 – Latest Research Trends and Future Prospects

- **Renaissance of Small Language Models:** Rise and optimization techniques of lightweight models

  - _Gemma 3 (1B~4B):_ Ultra-lightweight LLM series optimized to work smoothly on consumer devices
  - _Mistral NeMo 12B:_ 12B model implementing **128K token** context window through NVIDIA NeMo optimization (specialized for long conversations/document processing)
  - _MathΣtral 7B:_ Math-specialized model based on Mistral (achieving **74.59%** on MATH benchmark, approaching GPT-4 level)

- **Evolution of Reasoning Capabilities:** New attempts by LLMs for complex problem solving

  - _Long CoT:_ Reasoning technique utilizing very long Chain-of-Thought, performing **backtracking** and error correction when necessary
  - _PAL (Program-Aided Language Modeling):_ Improving numerical calculation or logical reasoning accuracy by combining code execution capabilities
  - _ReAct:_ Generating more accurate and factual answers by utilizing **external tools** (e.g., calculator, web search) during reasoning

- **Deployment and Optimization Frameworks:** Current status of tools for deploying lightweight/optimized LLMs

  - _llama.cpp:_ Lightweight C++ implementation enabling LLM execution on CPU
  - _MLC-LLM:_ WebGPU-based runtime supporting LLM inference on mobile/web browsers
  - _PowerInfer-2:_ Distributed inference framework maximizing power efficiency for large model inference

- **Student Presentations:** Review and present latest papers selected by groups, discuss significance, limitations, and future research directions of the research

### Week 14 – Final Project Development and MLOps

- **NLP Model MLOps:** Concepts and tools for NLP MLOps for actual service application

  - Model version management and A/B testing techniques
  - Building continuous learning pipelines utilizing user feedback
  - Real-time monitoring and performance degradation (drift) detection systems

- **Team Project Development:** Progress check of **prototype model** development for topics selected by each team
- **Industry Mentor Review:** Review sessions with invited industry mentors on project progress and feedback collection (industry requirement reflection, practicality evaluation, etc.)

### Week 15 – Industry Application Case Analysis and Final Presentations

- **Industry-specific NLP Success Cases:**

  - Healthcare: Clinical record automation NLP reducing doctor documentation burden from **49% → 27%** (utilizing healthcare domain-specific LLM)
  - Finance: Morgan Stanley's legal analysis bot COIN introduction reducing annual workload by **360,000 hours**
  - Education: Improving learning efficiency with personalized learning and multilingual support tutor AI (30% increase in student engagement)

- **Final Presentations:** Team project result presentations and demo demonstrations (sharing model architecture, demonstration results and limitations)
- **Course Comprehensive Discussion:** Overall summary of course content and Q&A, future prospects brainstorming (student feedback collection and future learning guidance)

## References

### Latest Architectures and Models

- Gu & Dao (2023). _Mamba: Linear-Time Sequence Modeling with Selective State Spaces._
- Peng et al. (2023). _RWKV: Reinventing RNNs for the Transformer Era._
- Lieber et al. (2024). _Jamba: A Hybrid Transformer-Mamba Language Model._

### Parameter-Efficient Learning

- Zhang et al. (2024). _WaveFT: Wavelet-based Parameter-Efficient Fine-Tuning._
- Liu et al. (2024). _DoRA: Weight-Decomposed Low-Rank Adaptation._
- Chen et al. (2024). _VB-LoRA: Vector Bank for Efficient Multi-Task Adaptation._

### Prompt Engineering and Evaluation

- Khattab et al. (2023). _DSPy: Compiling Declarative Language Model Calls._
- Liu et al. (2023). _G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment._
- Jain et al. (2024). _LiveCodeBench: Holistic and Contamination Free Evaluation._

### RAG and Knowledge Integration

- Zhang et al. (2024). _HippoRAG: Neurobiologically Inspired Long-Term Memory._
- Edge et al. (2024). _GraphRAG: A Modular Graph-Based RAG Approach._
- Chen et al. (2024). _Hybrid Retrieval-Augmented Generation: Best Practices._

### Alignment and Responsible AI

- Rafailov et al. (2023). _Direct Preference Optimization: Your Language Model is Secretly a Reward Model._
- Bai et al. (2022). _Constitutional AI: Harmlessness from AI Feedback._
- EU Commission (2024). _EU AI Act: Implementation Guidelines._

### Industry Applications and Deployment

- _Healthcare NLP Market Report 2024–2028_. Markets and Markets.
- _Financial Services AI Applications 2025_. McKinsey Global Institute.
- _State of AI in Education 2025_. Stanford HAI.

### Development Tools and Frameworks

- **CrewAI Documentation:** [https://docs.crewai.com/](https://docs.crewai.com/)
- **DSPy Official Guide:** [https://dspy-docs.vercel.app/](https://dspy-docs.vercel.app/)
- **OpenRLHF Project:** [https://github.com/OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)
