# Week 4: Advanced Prompting Techniques and Optimization

## 1. Systematic Prompting Techniques: Role Assignment and Structured Prompting

To enhance the performance of Large Language Models (LLMs), **prompt engineering** techniques have evolved significantly. Among these, **role prompting** and **structured prompting** are systematic methods for improving model response quality.

### 1.1 Role Prompting

**Role prompting** is a technique that assigns a specific **persona** or role to the model to adjust its response style and focus. For example, starting a prompt with "You are a history teacher. Explain the importance of the Industrial Revolution." causes the model to mimic the tone and perspective of a history teacher, providing more contextually appropriate explanations. Role prompting not only allows control over response tone and format but has also been reported to enhance the model's **reasoning performance**. In practice, specifying expert roles like "You are a mathematician..." can help the model perform **more consistent and accurate reasoning** on complex problems.

### 1.2 Structured Prompting

**Structured prompting** is a technique that writes prompts following clear **structure and steps** to guide the model to respond systematically. Unlike simple conversational prompts, structured prompts explicitly separate roles, tasks, and formats. For example, using the **"Role-Task-Format"** framework:

- **Role**: "As a history teacher,"
- **Task**: "explain the causes of World War I, and"  
- **Format**: "answer in bullet points that students can easily understand."

In addition to this **RTF framework**, various structured strategies such as **CIO (Context-Input-Output)** and **WWHW (Who-What-How-Why)** have been proposed. Structured prompts provide **clear instructions and output formats** to the model, making them effective for improving response **consistency** and **accuracy**. For cases requiring **structured output** like JSON format, reliable results can be obtained by presenting prompts field by field.

### 1.3 Practice Example: Structured Prompt Construction

```python
def create_structured_prompt(role, task, format_instruction, context=""):
    """
    Function to create structured prompts
    
    Args:
        role: Role to assign to the model
        task: Task to perform
        format_instruction: Output format instruction
        context: Additional context (optional)
    """
    prompt = f"""Role: {role}

Task: {task}

Format: {format_instruction}"""
    
    if context:
        prompt += f"\n\nContext: {context}"
    
    return prompt

# Example usage
role = "Experienced software developer"
task = "Please explain step-by-step how to set up a new web server"
format_instruction = "List each step with numbers and emphasize important parts"

prompt = create_structured_prompt(role, task, format_instruction)
print(prompt)
```

**Output Example:**
```
Role: Experienced software developer

Task: Please explain step-by-step how to set up a new web server

Format: List each step with numbers and emphasize important parts
```

Such systematic prompts help the model clearly understand the **role**, **objective**, and **format** for its response, enabling higher quality responses compared to scattered instructions.

## 2. Self-Consistency Technique and GSM8K Performance Improvement

In **Chain-of-Thought (CoT)** prompting for complex problems, model performance can be influenced by **initial path bias** since the model often follows only one reasoning path. **Self-Consistency** is a **decoding strategy** that addresses this problem by **sampling multiple reasoning paths** instead of a single response and determining the final answer through **voting**. In other words, it generates multiple **thought processes** for the same question (typically using temperature) and selects the **most consistently appearing final answer**.

The intuition behind this method is that "while thinking paths may differ for difficult problems, **the correct answer is one**." By applying Self-Consistency, the model explores various approaches and takes answers closer to the **intersection**, reducing errors from single paths and significantly improving performance on complex problems.

### 2.1 GSM8K Performance Improvement Case

Self-Consistency showed remarkable improvement on the **GSM8K** benchmark, which requires mathematical reasoning. According to Wang et al.'s (2022) research, applying **Self-Consistency decoding to CoT prompts** achieved a **17.9%p performance improvement** on GSM8K. For example, a model's GSM8K accuracy of 55% rose to approximately 72.9% after applying Self-Consistency. This technique also brought double-digit performance improvements to other reasoning tasks (SVAMP, AQuA, StrategyQA, etc.), and the effect was demonstrated in the representative paper published at ICLR 2023.

### 2.2 Self-Consistency Implementation Example

```python
import openai
from collections import Counter
import re

def extract_final_answer(text):
    """Function to extract final answer from text"""
    # Find answers using various patterns
    patterns = [
        r'answer is\s*(\d+)',
        r'the answer is\s*(\d+)',
        r'therefore\s*(\d+)',
        r'result is\s*(\d+)',
        r'(\d+)\s*is the answer',
        r'(\d+)\s*is correct'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Find the last number
    numbers = re.findall(r'\d+', text)
    return numbers[-1] if numbers else None

def self_consistency_sampling(question, model="gpt-3.5-turbo", num_samples=5):
    """
    Multi-sampling and voting through Self-Consistency
    
    Args:
        question: Math problem
        model: Model to use
        num_samples: Number of samples to generate
    """
    cot_prompt = f"""Solve the following math problem step by step.

Problem: {question}

Think step by step and provide the final answer at the end."""

    answers = []
    
    for i in range(num_samples):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": cot_prompt}],
                temperature=0.7,  # Use high temperature for diversity
                max_tokens=500
            )
            
            answer_text = response.choices[0].message.content
            final_answer = extract_final_answer(answer_text)
            
            if final_answer:
                answers.append(final_answer)
                print(f"Sample {i+1}: {final_answer}")
            
        except Exception as e:
            print(f"Error generating sample {i+1}: {e}")
    
    # Determine final answer through voting
    if answers:
        answer_counts = Counter(answers)
        most_common = answer_counts.most_common(1)[0]
        final_answer = most_common[0]
        confidence = most_common[1] / len(answers)
        
        print(f"\nFinal answer: {final_answer}")
        print(f"Confidence: {confidence:.2f} ({most_common[1]}/{len(answers)})")
        
        return final_answer, confidence
    
    return None, 0

# Usage example
question = "I bought 3 apples and 2 pears. Apples cost 500 won each and pears cost 700 won each. How much do I need to pay in total?"

final_answer, confidence = self_consistency_sampling(question, num_samples=5)
```

**Output Example:**
```
Sample 1: 2900
Sample 2: 2900
Sample 3: 2900
Sample 4: 2900
Sample 5: 2900

Final answer: 2900
Confidence: 1.00 (5/5)
```

### 2.3 Advantages and Limitations of Self-Consistency

**Advantages:**
- **Reduced uncertainty**: Explores multiple paths to reduce errors from single paths
- **Stable performance**: Provides more stable accuracy rates for math problems or commonsense reasoning
- **Simple implementation**: Only requires temperature adjustment and voting logic added to existing CoT prompts

**Limitations:**
- **Increased computational cost**: Multiple reasoning steps are required, increasing costs
- **Time delay**: May be unsuitable for cases requiring real-time responses
- **No consistency guarantee**: All samples may produce the same wrong answer

## 3. Tree of Thoughts Technique: Exploration for Complex Problem Solving

**Tree of Thoughts (ToT)** extends Chain-of-Thought by enabling the model to **explore multiple branches of thought in a tree structure**. The core concept of ToT, proposed by Yao et al. (2023), is to have the model generate intermediate problem-solving steps (thoughts) one by one while creating **multiple alternative branches** for exploration, and at each step, **self-evaluate** to select promising branches or prune unnecessary ones through backtracking. This allows LLMs to mimic **strategic forward-thinking (lookahead)** and explore more systematically even in complex problems.

The ToT algorithm is typically combined with **search techniques** like BFS/DFS. For example, when solving a problem requiring 3 intermediate thought steps, multiple candidate thoughts are created at step 1, **step 2 candidates are expanded for each**, and finally, by proceeding to step 3, the model **evaluates "solvability"** to select branches. The model indicates for each intermediate thought whether *"this path seems likely to lead to a solution (possible)"* or *"seems unlikely"*, **keeping only high-probability paths** to improve search efficiency.

### 3.1 Game of 24 Performance Improvement Case

ToT's power was dramatically demonstrated in the mathematical puzzle *24 Game*. The *24 Game* is a problem of finding an expression that makes 24 using all four given numbers. When GPT-4 was asked to solve it using only **traditional CoT prompts**, the success rate was only **4%**. However, when the **Tree of Thoughts strategy** was applied to the same GPT-4, the **success rate rose to 74%**. This shows that ToT dramatically increased the rate of reaching correct answers through exploration of multiple paths. According to research results, ToT showed superior performance compared to traditional CoT across **tasks requiring exploration and planning** such as creative writing and mini crosswords.

### 3.2 Tree of Thoughts Implementation Example

```python
import openai
from typing import List, Dict, Any
import json

class TreeOfThoughts:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.thoughts = []
        self.evaluations = []
    
    def generate_thoughts(self, problem: str, current_thoughts: List[str] = None) -> List[str]:
        """Generate possible next thoughts from current situation"""
        
        if current_thoughts is None:
            current_thoughts = []
        
        context = f"Problem: {problem}\n"
        if current_thoughts:
            context += f"Current thoughts: {' -> '.join(current_thoughts)}\n"
        
        prompt = f"""{context}

Please suggest 3-5 possible approaches for the next step to solve the above problem.
Each approach should be specific and actionable.

Format:
1. [Approach 1]
2. [Approach 2]
3. [Approach 3]
..."""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )
            
            thoughts_text = response.choices[0].message.content
            thoughts = self._parse_thoughts(thoughts_text)
            return thoughts
            
        except Exception as e:
            print(f"Error generating thoughts: {e}")
            return []
    
    def evaluate_thought(self, problem: str, thought_path: List[str]) -> float:
        """Evaluate the promise of a thought path (0-1 score)"""
        
        context = f"Problem: {problem}\n"
        context += f"Thought path: {' -> '.join(thought_path)}\n"
        
        prompt = f"""{context}

Please rate how promising this thought path is for solving the problem on a scale of 0-10.
Evaluation criteria:
- Logical consistency
- Problem-solving potential
- Feasibility

Answer with only the score number (e.g., 7)"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text) / 10.0  # Normalize to 0-1 range
            return score
            
        except Exception as e:
            print(f"Error during evaluation: {e}")
            return 0.0
    
    def solve_with_tot(self, problem: str, max_depth: int = 3, beam_width: int = 3) -> Dict[str, Any]:
        """Solve problem using Tree of Thoughts"""
        
        # Initial state
        current_paths = [[]]  # Start with empty path
        best_solution = None
        best_score = 0.0
        
        for depth in range(max_depth):
            print(f"\n=== Depth {depth + 1} ===")
            new_paths = []
            
            for path in current_paths:
                # Generate next thoughts from current path
                next_thoughts = self.generate_thoughts(problem, path)
                print(f"Path {path}: {len(next_thoughts)} candidates generated")
                
                for thought in next_thoughts:
                    new_path = path + [thought]
                    score = self.evaluate_thought(problem, new_path)
                    
                    print(f"  '{thought}' -> Score: {score:.2f}")
                    
                    new_paths.append((new_path, score))
                    
                    # Update best score
                    if score > best_score:
                        best_score = score
                        best_solution = new_path
            
            # Keep only top beam_width paths
            new_paths.sort(key=lambda x: x[1], reverse=True)
            current_paths = [path for path, score in new_paths[:beam_width]]
            
            print(f"Keeping top {beam_width} paths")
        
        return {
            "best_solution": best_solution,
            "best_score": best_score,
            "all_paths": current_paths
        }
    
    def _parse_thoughts(self, text: str) -> List[str]:
        """Parse thoughts from generated text"""
        thoughts = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbers or bullet points
                thought = line.split('.', 1)[-1].strip()
                if thought.startswith('- '):
                    thought = thought[2:].strip()
                if thought:
                    thoughts.append(thought)
        
        return thoughts

# Usage example
def solve_24_game(numbers: List[int]):
    """Solve 24 game"""
    problem = f"Find an expression that makes 24 using the given numbers {numbers}. Each number must be used exactly once."
    
    tot = TreeOfThoughts()
    result = tot.solve_with_tot(problem, max_depth=3, beam_width=3)
    
    print(f"\n=== Final Result ===")
    print(f"Best score: {result['best_score']:.2f}")
    print(f"Optimal path: {' -> '.join(result['best_solution'])}")
    
    return result

# Example execution
numbers = [4, 6, 8, 2]
result = solve_24_game(numbers)
```

**Output Example:**
```
=== Depth 1 ===
Path []: 4 candidates generated
  'First, try multiplying two numbers to make a large number' -> Score: 0.60
  'Try combining addition and subtraction' -> Score: 0.50
  'Use division' -> Score: 0.70
  'Try complex operations with parentheses' -> Score: 0.80

Keeping top 3 paths

=== Final Result ===
Best score: 0.90
Optimal path: Try complex operations with parentheses -> (8-4) * (6-2) = 4 * 4 = 16 -> 16 + 8 = 24
```

### 3.3 Advantages and Limitations of Tree of Thoughts

**Advantages:**
- **Systematic exploration**: Systematically explores multiple possibilities, increasing the likelihood of reaching optimal solutions
- **Backtracking**: Early abandonment of wrong paths improves efficiency
- **Complex problem solving**: Effective for complex problems that are difficult to solve with simple CoT

**Limitations:**
- **Computational cost**: Significantly increased costs due to exploring multiple paths
- **Evaluation subjectivity**: Consistency may be poor since the model evaluates itself
- **Implementation complexity**: More complex to implement than simple CoT

## 4. DSPy Framework: Declarative Prompt Programming

**DSPy** framework emerged as an innovative approach to make prompt engineering **more systematic and modular**. DSPy (Declarative **Self-Improving** Python) treats prompts as a kind of **program**, supporting **declarative** writing and automatic optimization. This allows describing and managing AI behavior through structured code instead of manually modifying prompt sentences one by one.

### 4.1 Core Components of DSPy

DSPy's **structure** consists of three core elements:

#### Signature
Declares the **input and output format** of the task to be solved. Like defining a function signature, it specifies what input fields to receive and what output fields to generate. For example, it can be expressed simply as a string like "question -> answer: float" or defined in detail through Python class inheritance. Signatures can specify **field types**, allowing DSPy to automatically generate prompt templates based on this and parse responses to the corresponding type.

#### Module
Encapsulates the **strategy** for generating prompts and calling models. It plays a role in selecting which prompting technique to use based on the Signature. DSPy provides various modules:

- **dspy.Predict**: Generates basic single question-answer frames
- **dspy.ChainOfThought**: Creates prompts that include both **intermediate reasoning and final answers** in Chain-of-Thought style
- **dspy.ReAct**: Constructs agent prompts applying tool usage and reactive reasoning (ReAct)
- **BestOfN, Parallel, Refine** and other modules for complex pipelines

When users select modules according to their signature, DSPy **assembles prompts** according to that strategy. For example, applying the ChainOfThought module to math problems automatically generates structured prompts like "**[[Problem]]**\n{question}\n**[[Solution]]**\n...**[[Answer]]**...".

#### Optimizer
DSPy's secret weapon, an algorithm that **automatically tunes** prompts (or model parameters). The Optimizer operates with (i) DSPy programs (combinations of modules), (ii) evaluation metrics (metric functions), and (iii) small amounts of training input. The Optimizer uses LLMs to generate better instructions or examples, and **searches and evaluates** multiple candidate prompts to improve prompts in the direction of maximizing performance.

For example, the **MIPROv2** optimizer initially collects **reasoning traces** by running programs on various inputs, selects high-scoring paths, and then modifies/proposes instructions based on this, finally finding optimal prompts through **combinatorial search**. Through this process, the Optimizer can automate **Few-shot example composition, instruction reconstruction, and fine-tuning** without manual tuning. DSPy includes various automatic prompt optimization algorithms such as **Bootstrap** series, **Ensemble**, and **SIMBA** in addition to MIPROv2.

### 4.2 DSPy Practice Example

```python
import dspy
from typing import Literal

# 1. Define signature
class SentimentCls(dspy.Signature):
    """Classify sentiment of a given sentence."""
    sentence: str = dspy.InputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()
    confidence: float = dspy.OutputField()

# 2. Create module
classifier = dspy.Predict(SentimentCls)

# 3. Usage example
result = classifier(sentence="This book was super fun to read, though not the last chapter.")
print(f"Sentiment: {result.sentiment}, Confidence: {result.confidence}")
```

**Output Example:**
```
Sentiment: positive, Confidence: 0.85
```

In the above code, the SentimentCls signature is defined and the dspy.Predict module is used to generate prompts. DSPy automatically describes input/output fields in the **system message** and constructs prompts by putting actual input values in the user message. The model's response is parsed by DSPy into **structured output** like result.sentiment, result.confidence. This makes prompt writing **reproducible** and **modular** at the code level, and can be easily connected to **performance improvement through Optimizer**.

### 4.3 Advantages and Limitations of DSPy

**Advantages:**
- **Modularity**: Can compose prompts into reusable components
- **Automatic optimization**: Can automatically improve prompts through Optimizer
- **Type safety**: Reduces errors by specifying input/output types
- **Reproducibility**: Manages prompts through code for reproducibility

**Limitations:**
- **Learning curve**: Must learn new concepts and paradigms
- **Limited modules**: Not all prompting techniques are provided as modules
- **Performance dependency**: Optimization results heavily depend on evaluation metrics

## 5. Automated Prompt Optimization (APE) and Latest Trends

Since manually experimenting and optimizing prompts is very cumbersome, research on **automated prompt optimization** is active. This is commonly called **Automated Prompt Engineering (APE)**, an approach that uses LLMs themselves to **search** or **evolve** optimal instructions or examples.

### 5.1 Automatic Prompt Engineer (APE)

The **Automatic Prompt Engineer (APE)** technique defines **prompt optimization as a program optimization problem**. Zhou et al.'s (2022) APE paper proposed a loop where **LLMs generate candidate instructions** and a separate verification model evaluates each candidate's performance to select the **highest performing prompt**. Through this method, superior performance compared to human-written prompts was shown across various NLP tasks, achieving human-designed prompt level or better results in 19 out of 24 tasks.

### 5.2 OPRO (Optimization by PROmpting)

**OPRO (Optimization by PROmpting)**, one of the latest research areas, is a method that uses **LLMs as optimization tools**. Instead of humans explicitly creating prompts, it transforms the problem into a **natural language optimization problem** of finding "**prompts that improve target performance**" and has LLMs generate progressively better prompts. For example, OPRO first summarizes previously generated prompts and their performance to present to the LLM, then receives **new prompts for the next iteration** in a repeating manner. This causes prompts to evolve in the direction of progressively improving scores.

### 5.3 Performance Improvement Cases

These automated techniques are significantly contributing to achieving **state-of-the-art performance**. Particularly on the **GSM8K** benchmark for math problems, APE-based methods have reached GPT-4 level performance. For example, the open-source **Ape** tool achieved **93% accuracy on GSM8K**, much higher than the same model's basic prompt performance (70%) or DSPy optimization performance (86%). Google researchers' OPRO technique also reported **8%p+ improvement in GSM8K accuracy compared to human-designed prompts**, achieving results close to SOTA, and achieved up to 50%p improvement even on challenging tasks like Big-Bench Hard.

In another interesting direction, frameworks like **PromptWizard** take a strategy of optimizing both prompts and few-shot examples together through LLM's **feedback-driven iteration**, and ideas like **PanelGPT** where multiple LLMs discuss and evaluate/improve prompts are being proposed. These tools and papers are all in the flow of maximizing model potential through **automated prompt improvement**.

### 5.4 Significance of Automated Prompt Optimization

In summary, automated prompt optimization (APE) can be called **"AutoML for prompts"** that emerged in the modern LLM era. This allows obtaining high-performance instructions with minimal human intervention, and open-source tools like **PromptChef/Ape**, **DSPy Optimizer**, and **PromptWizard** are publicly available to help researchers and developers.

## 6. Practice Example: DSPy-based Automated Prompt Optimization Pipeline

Finally, let's look at a practice example of constructing an **automated prompt optimization** pipeline using the DSPy framework introduced earlier. Here, we go through the steps of **problem definition → Signature/Module composition → improvement through Optimizer → performance verification** using a simple classification problem as an example.

### 6.1 Problem Definition

Let's consider a task that takes *historical event descriptions* as input and classifies the **field of the event**. Output labels are one of about 10 categories like "War/Conflict", "Politics/Governance", "Science/Technology". The model's output also includes **confidence scores** to check uncertainty.

### 6.2 Signature & Module Composition

First, define a signature class in DSPy.

```python
from typing import Literal
import dspy

# 1. Define signature
class CategorizeEvent(dspy.Signature):
    """Classify historic events into categories."""
    event: str = dspy.InputField()
    category: Literal["Wars", "Politics", "Science", "Culture", "Economics"] = dspy.OutputField()
    confidence: float = dspy.OutputField()

# 2. Create module
classifier = dspy.Predict(CategorizeEvent)

# 3. Initial performance evaluation (example)
test_events = [
    "World War II began in 1939",
    "Einstein published the theory of relativity",
    "The French Revolution occurred in 1789"
]

# 4. Automatic improvement through Optimizer
from dspy.teleprompt import MIPROv2

def validate_category(example, prediction):
    return 1.0 if example.category == prediction.category else 0.0

optimizer = MIPROv2(metric=validate_category, auto="light")
optimized_classifier = optimizer.compile(classifier, trainset=train_examples)

# 5. Performance improvement verification
result = optimized_classifier(event="Einstein published the theory of relativity")
print(f"Category: {result.category}, Confidence: {result.confidence}")
```

By declaring input (event) and output (category, confidence) fields in the Signature as above, DSPy creates **basic prompts** following that structure. The dspy.Predict module generates 0-shot prompts, so calling the model in this state performs classification tasks with **boilerplate prompts** that are not yet optimized.

### 6.3 DSPy Optimization Process

1. **Initial performance evaluation**: Measure performance (classification accuracy) on a small number of example inputs with the prepared classifier module. For example, let's assume that evaluating 20 historical event descriptions with correct labels for the above task resulted in about **52% accuracy**.

2. **Optimizer application**: Use DSPy's **MIPROv2** to optimize prompts. MIPROv2 is an algorithm focused on improving **the prompts themselves** without touching model weights. When compile is called, MIPROv2 internally performs the following:
   - Runs the classifier module on various inputs and collects model responses to measure current prompt performance
   - Uses LLMs to generate multiple **variation candidates** for prompt instructions or attempts few-shot example addition when necessary
   - Repeats mini-batch evaluation with various candidate prompts and **searches** in the direction of improving scores

3. **Performance improvement verification**: Apply the optimized module to the same evaluation set to measure performance again. For example, if **accuracy improved to 63%**, it's a significant improvement from the initial state. In actual cases, DSPy's optimizer has been reported to improve accuracy from **about 51.9% to 63.0%**.

Through this process, we can build **declarative prompt design** and **automated optimization** pipelines using DSPy. This approach is much more **efficient** than manually improving prompts and is a powerful tool that can **systematically enhance** model potential.

---

## Checkpoint Questions

1. What is the **Role Prompting** technique and how does it affect model responses? What should be considered when applying it?

2. How does **Self-Consistency decoding** work and why can it improve Chain-of-Thought prompting performance? Explain the performance improvement figures on GSM8K.

3. How does the **Tree of Thoughts (ToT)** technique perform problem solving? Mention the performance improvement ToT showed in the *Game of 24* puzzle.

4. What do **DSPy's Signature, Module, and Optimizer** each mean and what roles do they play? What advantages does using them provide for prompt engineering?

5. What is **Automated Prompt Optimization (APE)**? Explain the notable achievements APE techniques have accomplished compared to human-written prompts using GSM8K examples.

6. Briefly summarize the procedure for improving prompts using **DSPy and Optimizer** for a given problem (Signature definition → module execution → Optimizer application → result verification). Also explain the advantages of such automated optimization.

---

## References

### Key Papers and Research Materials

- Wang, X., et al. (2022). "Self-Consistency Improves Chain of Thought Reasoning in Language Models." arXiv preprint arXiv:2203.11171.
- Yao, S., et al. (2023). "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." arXiv preprint arXiv:2305.10601.
- Zhou, D., et al. (2022). "Large Language Models Are Human-Level Prompt Engineers." arXiv preprint arXiv:2211.01910.
- Yang, C., et al. (2023). "Large Language Models as Optimizers." arXiv preprint arXiv:2309.03409.

### Technical Documentation and Implementations

- DSPy Official Documentation: https://dspy.ai/
- Learn Prompting: https://learnprompting.org/
- Prompt Engineering Guide: https://www.promptingguide.ai/
- PromptWizard Framework: https://microsoft.github.io/PromptWizard/

### Online Resources and Blogs

- "Role Prompting: Guide LLMs with Persona-Based Tasks" - Learn Prompting
- "Prompt Architectures: An Overview of structured prompting strategies" - Medium
- "Tree of Thoughts (ToT)" - Prompt Engineering Guide
- "Pipelines & Prompt Optimization with DSPy" - Technical Blog
- "Best Free Prompt Engineering Tools of 2025" - SourceForge

### Benchmarks and Evaluation Materials

- GSM8K: Grade School Math 8K Dataset
- Game of 24: Mathematical Puzzle Benchmark
- Big-Bench Hard: Challenging Language Understanding Tasks
