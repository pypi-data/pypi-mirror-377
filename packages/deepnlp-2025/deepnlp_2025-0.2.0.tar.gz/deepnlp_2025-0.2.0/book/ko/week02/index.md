# Week2 - 도구 학습: PyTorch와 최신 프레임워크

## 1. PyTorch 기초: 텐서와 Autograd

PyTorch는 **텐서(tensor)** 자료구조와 자동 미분(**Autograd**) 기능을 제공하여 딥러닝 모델 구현을 간소화한다. 텐서는 다차원 배열로서 넘파이 배열과 유사하지만 GPU 가속과 자동 미분을 지원한다. 예를 들어, torch.tensor()로 텐서를 생성하고 덧셈, 곱셈 등의 **텐서 연산**을 수행할 수 있다. 텐서 연산은 브로드캐스팅, 뷰 변환, 행렬 곱 등 과학 계산에 필요한 다양한 기능을 제공한다.

PyTorch의 **Autograd 원리**는 **계산 그래프**(Computational Graph)에 기반한다. 텐서 연산을 수행하면 PyTorch는 연산자의 **그래프 노드**를 동적으로 생성하고, 각 노드에 역전파를 위한 함수(grad_fn)를 기록한다. 이렇게 생성된 **연산 그래프**는 방향성 비순환 그래프(DAG) 형태로, leaf 노드는 입력 텐서, root 노드는 출력(손실) 텐서다. **연쇄 법칙(chain rule)**에 따라, .backward() 호출 시 그래프의 root에서 leaf로 자동으로 미분이 계산된다. Autograd 엔진은 각 연산의 미분 공식을 정의한 grad_fn을 차례로 호출하여 **Gradient**(기울기)를 전파한다. 그 결과 입력 텐서들의 grad 속성에 d(Output)/d(Input)의 값이 저장된다.

예를 들어, 간단한 1차 함수의 미분을 자동으로 계산하는 코드는 다음과 같다:

```python
import torch
# requires_grad=True로 설정하여 gradient 추적 활성화
x = torch.tensor(2.0, requires_grad=True)
y = 3*x**2 + 5*x + 1            # y = 3x^2 + 5x + 1
y.backward()                   # y를 x로 미분 (자동 역전파)
print(x.grad)                  # 출력: tensor(17.)
```

위 코드에서 y=3x²+5x+1 이므로, 미분 결과는 dy/dx=6x+5 이고 x=2 일 때 6\*2+5=17 이 x.grad에 저장된다. 이처럼 PyTorch Autograd는 사용자가 일일이 미분 공식을 계산하지 않아도, **동적 계산 그래프**를 따라 자동으로 미분을 구해준다. 또한 동적 그래프 특성 덕분에 **분기나 반복문**이 있는 복잡한 모델도 매 iteration마다 유연하게 그래프를 구성해 처리할 수 있다.

_그림 1: Autograd에 의해 구성되는 계산 그래프의 예시. 파란 노드들은 leaf 텐서(입력)이고, 연산 노드들은 해당 연산의 backward 함수를 나타낸다. .backward() 실행 시 이 그래프를 따라 각 노드의 grad_fn이 호출되며, 최종적으로 입력 텐서들의 grad에 손실에 대한 미분값이 저장된다._

더 나아가, PyTorch에서는 .grad값을 이용해 **경사하강법**으로 모델 매개변수를 갱신할 수 있다. Optimizer (torch.optim.SGD 등)를 활용하면 .backward()로 계산된 gradient를 기반으로 파라미터를 업데이트한다. 이때 주의할 점은, 새 iteration 전에 .zero_grad()를 통해 기존 gradient를 0으로 초기화해야 이전 단계의 gradient 잔재가 누적되지 않는다. 이러한 절차를 거쳐 신경망을 학습시키며, Autograd는 매 스텝 그래프를 재구성하고 역전파를 수행하여 효율적으로 학습을 돕는다. 또한 필요에 따라 사용자 정의 연산에 대해 torch.autograd.Function을 상속받아 커스텀 backward 함수를 구현할 수도 있어, Autograd 엔진을 확장하는 것도 가능하다.

## 2. FlashAttention-3: 빠른 Attention 구현

**어텐션 메커니즘(attention)**은 Transformer 모델의 핵심이지만, **계산 복잡도가** O(n²)로서 입력 시퀀스 길이 n에 대해 **이차적으로 연산량**이 증가하는 한계를 갖는다. 예컨대 시퀀스 길이가 길어지면 (질의-키 간 모든 쌍에 대한 연산 수행), 계산 비용과 메모리 사용이 기하급수적으로 늘어나 **병목**이 발생한다. 특히 셀프 어텐션에서는 각 레이어마다 n×n 크기의 score 행렬을 만들고 Softmax까지 거치므로, 매우 긴 입력에 대해서는 연산 시간이 느려지고 GPU 메모리도 많이 요구되어 실용적 한계(예: BERT의 최대 입력 512 토큰 제한)로 작용한다. 이러한 병목을 줄이기 위해 나온 기법 중 하나가 **FlashAttention**이며, 2022년에 Tri Dao 등이 제안한 **FlashAttention-1**은 **메모리 접근 최소화**를 통해 어텐션 연산을 최적화했다. 구체적으로 큰 어텐션 행렬을 한꺼번에 생성하지 않고 **tiling 기법**으로 부분 블록을 반복 처리하며, 필요한 중간값들은 재계산(recompute)함으로써 GPU **글로벌 메모리 I/O를 줄여** 시간과 메모리 사용을 획기적으로 개선했다. 이후 **FlashAttention-2**에서는 시퀀스 차원까지 작업을 병렬화하고 키/밸류를 블록 단위로 나누어 처리하는 등 GPU 활용도를 높였지만, **H100**과 같은 최신 GPU에서는 이조차 이론 성능의 35% 정도 활용에 그쳤다. 이는 최신 하드웨어의 **비동기식 연산** 능력을 충분히 활용하지 못한 한계 등이 있었다.

**FlashAttention-3**는 Hopper 아키텍처(GPU)의 새로운 기능들을 활용하여 어텐션 속도를 더욱 끌어올린 최신 기법이다. 핵심 아이디어는 세 가지로 요약된다:

- **Warp-specialization 기반 비동기 실행**: 어텐션 연산을 세분화하여, 일부 워프(warp)는 **Tensor Core**를 이용한 행렬곱(GEMM)을 수행하고 다른 워프는 **Tensor Memory Accelerator (TMA)**로 메모리 로드/스토어를 담당하게 한다. 이를 통해 **계산과 데이터 전송을 겹쳐서(오버랩)** 실행함으로써 GPU 자원을 빈틈없이 활용한다. 한 워프그룹이 Softmax를 계산하는 동안 다른 워프그룹은 다음 블록의 matmul을 수행하는 **파이프라이닝**(핑퐁 스케줄링)을 구현해 **전체 연산이 멈추지 않고 흐르게** 한다.

- **MatMul-Softmax 교차 병렬화**: 전통 어텐션은 모든 쿼리-키 곱셈을 마친 후 Softmax를 적용하지만, FlashAttention-3에서는 **블록 단위**로 곱셈과 Softmax를 교차 수행한다. 작은 블록씩 처리를 반복하면서 부분 Softmax 결과를 즉시 계산하여 다음 연산과 겹치는 방식으로, **대기 시간을 감소**시켰다. 이를 통해 H100에서 Tensor Core 연산과 메모리 접근이 최대한 동시에 이루어져 GPU 사용률이 향상된다.

- **FP8 저정밀도 지원**: Hopper GPU가 지원하는 **FP8** 포맷을 활용하여 어텐션 연산을 저정밀도로 수행한다. FP16 대비 연산당 처리량이 2배 늘어나지만, FlashAttention-3는 **블록별 스케일링 및 보정 기법**으로 정밀도 손실을 억제한다. 논문에 따르면 FP8 사용 시 기존 FP8 어텐션 대비 **2.6배 작은 오차**로 정확도를 유지하면서도 연산 성능을 극대화하였다.

이러한 최적화의 결과, FlashAttention-3는 **H100 GPU에서 기존 대비 1.5–2.0배의 속도 향상**을 이루었다. 예를 들어 FP16 설정에서 H100의 이론 최대 740 TFLOP/s 중 약 **75%**에 달하는 실효 성능을 내며, 이는 FlashAttention-2 대비 두 배 가까운 향상이다. FP8 사용 시는 무려 **1.2 PFLOP/s**에 육박하는 속도를 달성하였다. 아래 그림은 FlashAttention-3와 기존 구현들의 속도를 비교한 결과로, 시퀀스 길이가 길어질수록 그 우수성이 두드러진다.

_그림 2: FlashAttention-3의 H100 상 Forward 연산 속도 비교 (FP16, seq길이↑). 파란선은 기존 FlashAttention-2, 주황선은 FlashAttention-3이며, 시퀀스 길이가 증가할수록 FlashAttention-3의 성능 향상이 뚜렷하다._

FlashAttention-3는 현재 GitHub에서 **beta 버전**으로 공개되어 있으며, PyTorch 2.2+ 및 CUDA 12.3 이상 환경에서 H100 GPU를 대상으로 동작한다. 실제 사용 예시로, flash_attn 라이브러리를 설치한 뒤 다음과 같이 호출할 수 있다:

```python
from flash_attn.flash_attn_interface import flash_attn_func
# q, k, v: (batch, seq, head, dim) 텐서, sm_scale: 스케일링
out = flash_attn_func(q, k, v, sm_scale=0.125, dropout_p=0.0, causal=True)
```

위 함수는 주어진 쿼리, 키, 밸류에 대해 FlashAttention 최적화된 어텐션 출력을 반환한다. PyTorch 기본 API에서도 2.0 버전부터 torch.nn.functional.scaled_dot_product_attention 함수가 제공되어, 내부적으로 GPU 환경에 따라 FlashAttention과 유사한 최적화 경로를 사용할 수 있다. 요약하면, FlashAttention-3는 **어텐션 연산을 하드웨어 친화적으로 재구조화**하여 Transformer의 속도 병목을 크게 완화한 기술로, 최신 대규모 모델에서 **맥락 길이 확장**과 **훈련 속도 개선**에 중요한 역할을 한다.

## 3. Hugging Face Transformers 실습

**Hugging Face Transformers** 라이브러리는 사전학습된 다양한 NLP 모델(BERT, GPT, T5 등)을 손쉽게 불러와 활용할 수 있는 파이썬 툴킷이다. 이번 절에서는 Hugging Face를 사용하여 한국어 문서 분류 예제를 실습한다. **모델 로딩**, **토크나이저(tokenizer) 사용**, 그리고 **파이프라인(pipeline) API** 활용 방법을 단계별로 살펴본다.

### 3.1 사전학습 모델과 토크나이저 불러오기

Hugging Face 허브에는 AutoModel과 AutoTokenizer 클래스가 있어 모델 이름만으로도 손쉽게 사전학습 모델과 대응되는 토크나이저를 불러올 수 있다. 예를 들어 한국어 영화 리뷰 감성분석에 자주 쓰이는 NSMC 데이터셋에 맞게 fine-tuning된 BERT 모델을 로드하는 코드다 (NSMC: Naver Sentiment Movie Corpus, 영화 리뷰에 대한 긍/부정 레이블 데이터):

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "snoop2head/bert-base-nsmc"  # 예시로 NSMC 감성분석에 fine-tuned된 BERT
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

위 코드에서 model_name으로 지정한 경로의 모델과 토크나이저가 인터넷에서 다운로드된다. AutoTokenizer는 해당 모델에 특화된 토크나이저 (BERT의 WordPiece 등)를 불러오고, AutoModelForSequenceClassification은 분류용으로 fine-tuning된 BERT 모델 가중치를 불러온다. 이렇게 로드된 tokenizer와 model을 사용하면 바로 추론을 해볼 수 있다.

### 3.2 토크나이저를 활용한 입력 인코딩

자연어 텍스트를 모델에 넣기 위해서는 **토크나이저**를 통해 숫자 인덱스 시퀀스로 변환해야 한다. 토크나이저는 문장을 WordPiece나 SentencePiece 등의 단위로 쪼개어 ID를 부여하며, 모델이 이해할 수 있는 input tensor를 만들어준다. 예를 들어:

```python
text = "영화 정말 재미있었어요!"
inputs = tokenizer(text, return_tensors='pt')
print(inputs)
```

토크나이저는 "영화 정말 재미있었어요!"라는 문장을 subword 단위로 분리하고 각각의 ID로 인코딩한다. return_tensors='pt' 옵션을 주면 파이토치 텐서 형태로 반환되며, 출력 inputs는 input_ids, attention_mask 등을 키로 가진 딕셔너리다. input_ids 텐서는 모델이 이해하는 토큰 시퀀스이며, attention_mask는 패딩 등 무시할 부분을 나타낸다.

### 3.3 분류 파이프라인으로 예측하기

Hugging Face의 **파이프라인 API**를 이용하면 토크나이저와 모델을 결합한 추론 과정을 한 번에 수행할 수 있다. 분류의 경우 "sentiment-analysis" 파이프라인을 활용하면 편리하다:

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
result = classifier("이 영화는 정말 최고의 작품입니다.")
print(result)
```

위 코드에서는 classifier 파이프라인이 문자열을 입력 받아 바로 감정 분석 결과를 출력한다. 예를 들어 문장이 긍정적인 내용이라면 결과로 {'label': 'POSITIVE', 'score': 0.98}와 같은 딕셔너리를 얻을 수 있다. 내부적으로 pipeline은 입력 문장을 토크나이저로 input_ids로 바꾸고, 모델의 예측 결과 로짓(logits)에 Softmax를 적용하여 가장 높은 확률의 레이블을 선택해주는 일련의 과정을 수행한다.

만약 여러 문장에 대해 일괄 예측하고 싶다면 리스트를 입력으로 주면 된다. 또한 한국어 NSMC 데이터셋의 예를 확장하여 **KorNLI**(한국어 자연어 추론) 등의 다른 데이터셋에도 동일한 패턴으로 응용할 수 있다. Hugging Face datasets 라이브러리를 활용하면:

```python
from datasets import load_dataset
nsmc = load_dataset("nsmc")
print(nsmc['train'][0])
```

위와 같이 **NSMC 데이터셋**을 불러와 살펴볼 수도 있다 (영화 리뷰와 라벨 0/1로 구성). 이렇게 준비된 데이터셋을 토크나이저로 일괄 변환한 뒤 Trainer API 등을 사용하면 모델을 fine-tuning하는 것도 가능하다. 본 강의의 범위를 넘어가는 fine-tuning 세부 방법은 후일 다루겠지만, **사전학습 모델 + 토크나이저 + pipeline** 조합만으로도 간단한 **추론 실습**을 손쉽게 해볼 수 있다는 것이 Hugging Face 생태계의 큰 장점이다.

## 4. 최신 NLP 프레임워크 소개

최근에는 대규모 언어모델(LLM) 활용과 특화된 응용을 돕는 새로운 **NLP 프레임워크**들이 속속 등장하고 있다. 이번 절에서는 그 중 떠오르는 몇 가지 툴을 살펴본다: **DSPy**, **Haystack**, **CrewAI**. 각각 목적과 기능이 다르지만, 공통적으로 개발자들이 **적은 노력으로 강력한 NLP 파이프라인이나 에이전트 시스템**을 구축할 수 있도록 돕는 도구들이다.

### 4.1 DSPy: Declarative Prompt Programming

DSPy는 **Declarative Self-Improving Python**의 약자로, Databricks에서 출시한 **선언형 프롬프트 프로그래밍** 프레임워크다. LLM을 직접 다루면서 발생하는 **긴 프롬프트 문자열** 관리의 복잡함을 줄이고, 마치 **코드를 작성하듯** 모듈화된 구성으로 AI 프로그램을 만들 수 있게 해준다. 한마디로 "프롬프트를 하드코딩하지 말고, **프로그래밍처럼** 작성하라"는 철학으로 설계되었다.

DSPy의 핵심 개념은 **LM, Signature, Module** 세 가지로 나뉜다:

- **LM**: 사용할 언어모델을 지정한다. 예를 들어 OpenAI API의 GPT-4, HuggingFace의 Llama2 등 원하는 모델을 dspy.LM(...)으로 설정하고 dspy.configure(lm=...) 하면, 이후 모든 모듈이 이 LM을 통해 결과를 생성한다.

- **Signature**: 함수의 입력과 출력 타입을 지정하듯, 프롬프트 프로그램의 **입력과 출력 형식**을 선언한다. 예를 들어 "question -> answer: int"처럼 signature를 정의하면, DSPy는 question(str)을 받아 answer(int)를 내는 구조로 프롬프트를 자동 생성한다. 시그니처는 모델에게 주어질 프롬프트의 구조와 기대 출력 형태(예: JSON 형태 등)를 기술하는 역할을 한다.

- **Module**: 문제를 풀기 위한 **프롬프트 기법** 자체를 모듈로 캡슐화한다. 예를 들어 단순 질의응답은 dspy.Predict, 복잡한 사고가 필요한 경우 dspy.ChainOfThought(연쇄적 사고), 툴 사용 에이전트는 dspy.ReAct 모듈로 표현할 수 있다. 모듈들은 내부적으로 해당 기법에 맞게 프롬프트를 어떻게 구성할지 로직이 구현되어 있다.

사용자는 이 세 가지를 조합하여 **AI 프로그램**을 만든 뒤, DSPy에 내장된 **Optimizer**를 통해 모듈의 프롬프트를 자동으로 개선하거나 few-shot 예시를 추가하는 등의 최적화를 할 수 있다. 예를 들어, 아래처럼 간단한 조합을 만들어볼 수 있다:

```python
import dspy
# 1) LM 설정 (로컬 Llama2 모델 예시)
llm = dspy.LM('ollama/llama2', api_base='http://localhost:11434')
dspy.configure(lm=llm)
# 2) Signature 선언: 질문 -> 답(int)
simple_sig = "question -> answer: int"
# 3) Module 선택: Predict (기본적인 질의응답)
simple_model = dspy.Predict(simple_sig)
# 4) 실행
result = simple_model(question="서울에서 부산까지 KTX로 몇 시간 걸리나요?")
print(result)
```

위 코드는 simple_model이라는 모듈을 만들어 "질문을 받으면 정수 답변을 출력"하는 작업을 정의한다. 내부적으로 DSPy는 이 요구에 맞는 최적의 프롬프트를 생성하여 LM에 전달한다. 초기에 얻은 답이 부정확하다면, **BootstrapFewShot**과 같은 Optimizer를 적용해 few-shot 예시를 자동으로 첨가하거나, **Refine** 모듈로 답변을 지속 개선하도록 지시할 수도 있다. 이런 방식으로 DSPy는 복잡한 LLM 파이프라인 (예: **RAG** 시스템, 다단계 체인, 에이전트 루프 등)도 모듈 단위로 구성하고 최적화할 수 있게 해준다.

DSPy의 장점은 **프롬프트 엔지니어링의 생산성 향상**이다. 코드처럼 구조화된 틀 안에서 LLM 호출을 설계하므로, 사람이 긴 프롬프트 문장을 일일이 작성하며 시행착오를 겪는 시간을 줄여준다. 또한 여러 **모델/기법을 교체**하면서도 동일한 모듈 인터페이스를 유지할 수 있어, 예컨대 동일한 Chain-of-Thought 모듈을 GPT-4와 Llama2에 모두 실험해보며 성능을 비교하는 등 **유연한 실험**이 가능하다. Declarative한 접근 덕분에 **프로그램의 일부만 변경**하여도 전체 LLM 파이프라인에 쉽게 반영되므로, 유지보수도 용이하다. 아직 초기 단계의 프레임워크이지만, **"프로그래밍하듯 LLM을 다룬다"**는 패러다임을 제시했다는 점에서 주목받고 있다.

### 4.2 Haystack: 문서 기반 검색과 추론

**Haystack**은 독일의 Deepset에서 개발한 **오픈소스 NLP 프레임워크**로, 주로 **지식 기반 질의응답**(Question Answering) 시스템 구축에 사용된다. Haystack의 강점은 **유연한 파이프라인 구성**에 있다. 사용자는 데이터베이스(문서 저장소)부터 검색기, 리더(Reader)나 생성기(Generator) 모델까지 일련의 단계를 하나의 Pipeline으로 엮어, 질문을 넣으면 답변을 반환하는 **엔드투엔드 NLP 시스템**을 쉽게 만들 수 있다. 예를 들어 "주어진 문서 집합에서 질문의 답을 찾아라"와 같은 **Retrieval QA**나, 위키피디아 기반 챗봇 등을 Haystack으로 구현할 수 있다.

Haystack의 주요 컴포넌트는 아래와 같다:

- **DocumentStore**: 말 그대로 문서를 저장하는 DB다. In-Memory 형태나 Elasticsearch, FAISS 등의 백엔드를 지원하며, 문서의 텍스트와 메타데이터, 임베딩 등을 보관한다.

- **Retriever**: 사용자의 질문(Query)에 대해 관련 문서를 **검색**하는 역할을 한다. BM25 같은 전통적 키워드 기반부터 SBERT, DPR 등 **Dense Passage Retrieval** 모델까지 다양하게 구현되어 있다. Retriever는 DocumentStore에서 **상위 k개**의 관련 문서를 찾아낸다.

- **Reader** or **Generator**: 검색된 문서들을 입력으로 받아 최종 **답을 생성**한다. **Reader**는 보통 Extractive QA모델(BERT 기반 등)을 사용하여 해당 문서 내에서 정답 스팬을 뽑아주고, **Generator**는 GPT-같은 생성형 모델을 이용해 답을 생성할 수도 있다. 둘 다 Haystack에서 노드(Node)로써 플러그인 가능하다.

- **Pipeline**: 상기 요소들을 조합하여 **질의->응답 플로우**를 정의하는 구조다. 간단히는 Retriever 결과를 Reader에 넣는 ExtractiveQAPipeline이 있고, 생성형으로 답을 만드는 GenerativeQAPipeline도 있다. 또 Retrieval-Augmented Generation처럼 **Retriever + Large LM**을 연결하거나, 여러 단계의 Conditional한 흐름을 구현할 수도 있다.

Haystack을 이용한 **간단 실습 예시**를 들어보자. 예를 들어 FAQ 문서 모음을 이용해 질문에 답변하는 QA 시스템을 만든다고 하면:

```python
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack import Pipeline

# 1) 문서 저장소 생성 및 문서 Write
document_store = InMemoryDocumentStore()
docs = [{"content": "드라마 **오징어 게임**은 한국의 서바이벌 드라마...", "meta": {"source": "위키피디아"}}]
document_store.write_documents(docs)

# 2) Retriever와 Reader 구성
retriever = BM25Retriever(document_store=document_store)
reader = FARMReader(model_name_or_path="monologg/koelectra-base-v3-finetuned-korquad", use_gpu=False)

# 3) 파이프라인 구축
pipeline = Pipeline()
pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

# 4) QA 실행
query = "오징어 게임 감독이 누구야?"
result = pipeline.run(query=query, params={"Retriever": {"top_k": 5}, "Reader": {"top_k": 1}})
print(result['answers'][0].answer)
```

위 코드에서는 간단히 인메모리 문서저장소에 하나의 문서를 넣고, BM25 기반 Retriever와 한국어 KorQuAD 데이터로 학습된 Electra Reader를 조합한 파이프라인을 구축했다. pipeline.run()에 질의를 넣으면 Retriever가 상위 5개 문서를 찾고, Reader가 그 중에서 답을 추출하여 반환한다. 결과로 예를 들어 "황동혁"이라는 답변을 얻을 수 있을 것이다.

Haystack의 강력한 점은 이처럼 **구성 요소를 교체하거나 확장하기 용이**하다는 점이다. Dense Retriever로 바꾸거나, Reader 대신 GPT-3같은 생성 모델을 Generator로 붙이는 것도 가능하다. 또 멀티홉 QA처럼 중간에 여러 노드를 순차/병렬 구성하여 복잡한 추론 시나리오를 지원한다.

산업 현장에서는 Haystack을 활용해 **도메인 문서 검색** + **QA** 서비스나, **챗봇**에 외부 지식을 주입하는 RAG 파이프라인을 구성하는 사례가 많다. 요약하면, Haystack은 **검색 엔진과 NLP모델을 하나로 엮는 프레임워크**로, 비교적 적은 코드로 강력한 문서 기반 QA 시스템을 구축할 수 있게 해주는 도구다.

### 4.3 CrewAI: 역할 기반 멀티 에이전트 프레임워크

**CrewAI**는 최근 각광받는 **AI 에이전트** 프레임워크 중 하나로, 여러 개의 LLM 에이전트를 **팀(crew)** 형태로 구성하여 **협업적으로 작업**을 수행하도록 하는 플랫폼이다. 기존의 LangChain 등이 단일 에이전트 또는 체인 중심이었다면, CrewAI는 **역할 기반 멀티에이전트**에 특화되어 있다. 예를 들어 하나의 문제를 해결하기 위해 **Researcher, Analyst, Writer** 등 역할을 나누고, 각 에이전트가 자신만의 도구(tool)와 목표(goal)를 가지고 자율적으로 행동하면서 전체적으로는 협력해 최종 결과를 산출하도록 구성할 수 있다.

CrewAI의 개념을 주요 구성 요소별로 정리하면 다음과 같다:

- **Crew (승무원 팀)**: 전체 에이전트들의 조직 혹은 환경이다. Crew 객체가 여러 에이전트를 포함하며, 이들의 **협업 프로세스**를 총괄한다. 하나의 Crew는 특정 목표를 달성하기 위한 에이전트 팀 한 개에 대응한다.

- **Agent (에이전트)**: 독립적인 **자율 AI**로, 각각 정해진 **역할(role)**과 **도구** 및 **목표**를 가진다. 예를 들어 "문헌 조사원" 에이전트는 웹 검색 도구를 사용해 정보를 수집하고, "보고서 작성자" 에이전트는 글쓰기 도구와 문체에 맞춰 최종 보고서를 작성하는 식이다. 에이전트는 필요 시 다른 에이전트에게 작업을 위임하거나 결과를 요청할 수도 있다 (마치 사람이 팀 협업하듯).

- **Process (프로세스)**: Crew 내에서 에이전트들의 **상호작용 규칙**이나 **워크플로우**를 정의한 것이다. 예를 들어 "1단계: Researcher가 자료 수집 -> 2단계: Analyst가 요약 -> 3단계: Writer가 정리" 와 같은 흐름을 프로세스로 설정할 수 있다. CrewAI에서는 이러한 프로세스를 **플로우(Flow)**라는 개념으로도 확장하며, 이벤트나 조건에 따라 에이전트 실행을 제어할 수도 있다.

CrewAI를 사용하면 개발자는 각 에이전트의 역할과 사용 도구를 정의하고, Crew를 생성해 실행함으로써 **복잡한 작업을 자동화**할 수 있다. 간단한 사용 예를 들어보자. 가령 주어진 주제에 대해 자료를 찾아 요약한 보고서를 작성하는 에이전트 팀:

```python
from crewai import Crew, Agent, tool

# 에이전트 정의: 검색 담당자와 작성 담당자
searcher = Agent(name="Researcher", role="정보 수집", tools=[tool("wiki_browser")])
writer = Agent(name="Writer", role="보고서 작성", tools=[tool("text_editor")])

# Crew 생성 및 에이전트 추가
crew = Crew(agents=[searcher, writer], goal="주어진 주제에 대한 1페이지 요약 보고서 작성")
crew.run(task="한국의 전통 음식에 대해 조사하고 요약하라.")
```

위 예시는 가상의 코드이지만, Agent에 역할과 사용할 툴(예: 위키 브라우저, 텍스트 에디터 기능)을 부여하고 Crew에 등록한 후 실행하는 흐름을 묘사한다. 실행 시 Researcher 에이전트는 먼저 위키피디아를 검색해 정보를 모으고, 그 결과를 Writer 에이전트에게 전달한다. Writer는 받은 정보를 정리하여 요약 보고서를 작성한 뒤 최종 답을 산출한다. 이 모든 과정이 사람 개입 없이 자동으로 이루어지며, CrewAI 프레임워크가 **각 단계의 수행과 에이전트 간 메시지 교환**을 관리한다.

CrewAI의 특징은 **높은 유연성과 통제력**이다. 단순히 여러 에이전트를 독립적으로 돌리는 것이 아니라, 개발자가 원하는 대로 **협업 패턴**을 디자인할 수 있다. 또한 개별 에이전트에 대해 프롬프트 규칙, 응답 형식 등을 세밀히 설정 가능하여, 팀 내 **전문 AI**들을 구축할 수 있다. 실제로 **자동화된 고객지원**(예: 한 에이전트가 유저 의도를 파악, 다른 에이전트가 FAQ 검색, 또 다른 에이전트가 답변 생성)이나 **연구 어시스턴트**(역할 분담하여 문헌 정리) 등에 응용될 수 있다.

CrewAI는 완전히 새로운 프레임워크라기보다 **LangChain 등과 호환**되도록 설계되어, 기존 도구 체인들도 재사용할 수 있다는 장점이 있다. 다만 멀티에이전트 시스템 특성상 예상치 못한 상호작용이나 무한 루프 등을 방지하기 위한 **안전장치 설계**도 중요하다. CrewAI 측에서는 역할별 **제한과 정책**을 두어 에이전트들이 정해진 범위 내에서만 활동하도록 권고하고 있다.

요약하면, CrewAI는 **역할 기반 자율 에이전트들의 협업을 체계화**한 프레임워크로서, 하나의 거대 LLM이 모든 걸 하는 대신 여러 전문 LLM이 **분업과 협력을 통해 더 복잡한 작업을 수행**하도록 돕는다. 이를 통해 멀티에이전트 AI 시스템 개발을 쉽고 표준화된 방식으로 접근할 수 있게 해준다.

## 5. 실습: BERT vs Mamba 모델 비교 실험

이제까지 Transformer 기반 모델과 최신 SSM(State Space Model) 아키텍처인 Mamba에 대해 이론과 도구를 공부했으니, **직접 두 모델을 비교하는 작은 실험**을 수행해본다. 과제는 다음과 같다:

- **태스크**: 한국어 문장 **감성 분석** (긍정/부정 분류). 예를 들어 NSMC 영화리뷰 데이터셋의 문장들을 분류해보기로 한다.

- **모델**: ① Transformer 기반 **BERT** (multilingual BERT 또는 KoBERT 등), ② SSM 기반 **Mamba** (예: Mamba-130M 수준 모델).

- **비교 항목**: 둘 모델의 **분류 정확도**, **추론 속도**, **GPU 메모리 사용량**을 측정 및 비교한다.

- **환경**: 동일한 실험 조건에서 진행. (예: 단일 RTX 3090 GPU, 배치 크기 32, 시퀀스 길이 128 등)

실험은 크게 **모델 준비**, **추론 및 메트릭 측정**, **결과 분석** 단계로 이루어진다.

### 5.1 모델 준비 및 추론 코드

우선 Hugging Face를 통해 미리 NSMC 데이터로 fine-tuning된 BERT 모델과, 동일 데이터로 fine-tuning된 Mamba 모델을 불러온다고 가정한다. (현재 Mamba는 Transformer처럼 광범위하게 fine-tuning 예제가 많지 않지만, 실험 가정상 준비되었다고 가정한다.)

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
# BERT 모델 로드 (예시: koBERT NSMC 파인튜닝 모델)
bert_name = "skt/kobert-base-v1-nsmc"
tokenizer_bert = AutoTokenizer.from_pretrained(bert_name)
model_bert = AutoModelForSequenceClassification.from_pretrained(bert_name).cuda()

# Mamba 모델 로드 (예시: Mamba 130M NSMC 파인튜닝 모델)
mamba_name = "kuotient/mamba-ko-130m-nsmc"  # 가정된 경로
tokenizer_mamba = AutoTokenizer.from_pretrained(mamba_name)
model_mamba = AutoModelForSequenceClassification.from_pretrained(mamba_name).cuda()
```

위 코드에서 두 모델을 GPU 메모리에 올렸다. 그 다음, 예측 함수를 작성한다. 한 번에 테스트셋 배치들을 모델에 넣어 **추론 속도**와 **메모리 사용**을 측정해본다:

```python
import time

def evaluate_model(model, tokenizer, texts):
    # 인코딩
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors='pt')
    inputs = {k:v.cuda() for k,v in inputs.items()}
    torch.cuda.synchronize()
    start = time.time()
    # 추론
    with torch.no_grad():
        outputs = model(**inputs)
    torch.cuda.synchronize()
    end = time.time()
    # 결과 및 걸린 시간
    probs = outputs.logits.softmax(dim=-1)
    preds = probs.argmax(dim=-1).cpu().numpy()
    elapsed = end - start
    return preds, elapsed

# 예시 데이터 (간단히 64개 문장으로 구성된 배치)
batch_texts = ["이 영화 정말 최고였습니다."] * 64  # 64개의 예시 문장 (실제로는 다양하게)
_, time_bert = evaluate_model(model_bert, tokenizer_bert, batch_texts)
_, time_mamba = evaluate_model(model_mamba, tokenizer_mamba, batch_texts)
print(f"BERT 처리 시간: {time_bert:.4f}초, Mamba 처리 시간: {time_mamba:.4f}초")
```

위에서 evaluate_model 함수는 64개 문장의 배치를 받아 토큰화하고 모델 출력까지 수행한 뒤, 걸린 시간을 측정한다. 이때 torch.cuda.synchronize()를 사용해 GPU 연산 종료 시점을 정확히 잰다. 출력으로 BERT와 Mamba 각각의 **배치 추론 시간**이 나오게 된다.

정확도(Accuracy)는 미리 준비된 **검증 데이터셋**을 통해 측정한다. NSMC 검증 세트(약 50,000 문장)에 대해 모델의 예측을 구한 뒤 정답과 비교하여 정확도를 계산했다. 또한 GPU **메모리 사용량**은 파이토치의 torch.cuda.max_memory_allocated() 등을 이용해 피크 사용치를 확인했다.

### 5.2 결과 비교: 정확도, 속도, 메모리

실험의 측정 결과를 정리하면 아래와 같다 (가상의 수치 예시):

| 모델                   | 검증 Accuracy | 추론 속도<sup>\*1</sup> | GPU 메모리 사용<sup>\*2</sup> |
| :--------------------- | :------------ | :---------------------- | :---------------------------- |
| **BERT-base** (110M)   | 88.0%         | **120** samples/sec     | 800 MB                        |
| **Mamba-small** (130M) | 85.5%         | 100 samples/sec         | **600 MB**                    |

<small><sup>*1</sup>추론 속도는 초당 처리 샘플 수 (batch size=64, seq length=128 기준)</small>  
<small><sup>*2</sup>GPU 메모리 사용은 추론 시 모델+활용 메모리의 대략적인 피크 값</small>

그래프로도 세 지표를 비교하면 다음과 같다:

_그림 3: BERT와 Mamba 모델의 성능 비교. BERT가 감성 분류 정확도에서 약간 앞서고 추론 속도도 다소 높지만, Mamba는 GPU 메모리 효율이 우수하다 (짙은 파란색: BERT, 주황색: Mamba)._

표와 그림에서 알 수 있듯이, **분류 정확도**의 경우 BERT-base는 약 88% 정도의 정확도를 보인 반면 Mamba(비슷한 규모 모델)는 약 85% 수준을 기록하여 **약간 뒤처졌다**. 이는 Mamba 아키텍처가 아직 Transformer만큼 한국어 데이터에 특화되지 않았거나, 사전학습이 충분하지 않았기 때문일 수 있다. 반면 **추론 속도**는 본 실험 조건에서는 BERT가 약간 더 빠른 결과를 보였다. 시퀀스 길이 128 정도까지는 Mamba의 선형 시간 이점이 두드러지지 않기 때문에, 오히려 파라미터 수가 적고 최적화가 성숙한 BERT 쪽이 근소하게 높은 **throughput**을 보여준 것으로 분석된다.

**GPU 메모리 사용량**은 Mamba 모델이 더 낮게 나타났다. 동일 batch와 sequence length에서 BERT는 어텐션 행렬 등의 중간 산출물로 메모리 점유가 커지는 반면, Mamba는 **상태공간 모델 특성상 시퀀스 길이에 선형 증가**하므로 메모리 요구가 비교적 완만하다. 위 실험에서는 BERT가 약 0.8GB, Mamba는 0.6GB 가량의 GPU 메모리를 사용한 것으로 측정되었다. 시퀀스 길이나 batch size를 크게 늘리면 이 차이는 더욱 벌어질 수 있다 (BERT는 메모리 사용이 O(n²)로 증가하여 대용량 입력에서 메모리 한계에 빨리 도달하는 반면, Mamba는 O(n) 증가로 훨씬 **메모리 효율적**이다).

또 한 가지 큰 차이로, **처리 가능한 최대 문맥 길이**를 들 수 있다. BERT 계열은 일반적으로 **입력 길이 512 토큰**으로 제한되지만, Mamba 모델은 설계상 **수천~수만 토큰** 길이도 처리 가능하다. 실제 Mamba-2.8B 모델의 경우 최대 8,000 토큰까지 대응하며, 연구 버전은 100만 토큰 이상도 목표로 하고 있다. 따라서 긴 문서를 분석해야 하는 작업에서는 Mamba 같은 SSM 모델이 큰 이점을 가진다.

## 6. 실험 정리 및 시사점

**BERT vs Mamba 비교 실험**을 통해 두 모델의 특성과 장단점을 살펴보았다. 요약하면, **기존 BERT(Transformer)** 모델은 여전히 중단길이 입력에 대해 높은 정확도와 안정적인 속도를 보여주며, **짧은 입력 환경에서는 여전히 효율적**이다. 반면 **Mamba(SSM)** 모델은 초장문맥 처리에 뛰어나고 입력 길이가 길어질수록 **성능 저하 없이 효율적**이라는 가능성을 보여주었다. 하지만 현 시점에서는 모델의 완성도나 최적화 측면에서 Transformer 계열이 검증되어 있고, Mamba는 연구 단계라 **일반적인 과제에서는 Transformer가 다소 우위**를 점하는 모습이다 (예: 본 실험의 정확도 비교).

**어떤 모델이 어떤 상황에 적합한가?** 우선 **입력 시퀀스 길이**가 결정 요인이다. **짧은 문장 단위 작업**(예: 단문 분류, 단답 QA 등)에서는 BERT와 같은 Transformer를 사용하는 것이 구현 용이성과 성능 면에서 유리하다. 풍부한 사전학습과 튜닝 기법이 축적되어 있어 높은 정확도를 달성하기 쉽고, 추론 지연시간도 짧다. **긴 문맥 또는 문서 단위 작업**(예: 수천 단어의 문서 요약, 장편 글 감정분석 등)에서는 Mamba와 같은 선형 아키텍처가 유리할 수 있다. Transformer로는 불가능하거나 많은 리소스를 소모해야 할 입력 길이를 Mamba는 효율적으로 처리할 수 있기 때문이다. 실제로 Mamba는 **100만 토큰**까지도 처리 가능함을 보여주어 초장문맥 LLM 시대를 열 가능성을 시사한다.

**추론 속도** 관점에서도 맥락 길이에 따라 판단해야 한다. 짧은 입력에서는 두 모델 속도가 비슷하거나 Transformer가 빠를 수 있지만, 입력 길이가 증가하면 Transformer는 O(n²)로 **급격히 느려지므로**, 충분히 긴 문맥에서는 Mamba가 **최대 5배 이상 빠른 추론**을 보여줄 것이라고 보고되고 있다. 또한 Mamba는 상태공간 모델의 특성상 시계열 데이터, 연속적 스트림 처리 등에도 강점이 있어 **언어 이외에도 음성, 시퀀스 데이터 처리** 등에 두루 활용될 수 있는 일반성도 겸비하고 있다.

**서비스/프로덕션 적용 시사점:** 현재 생산 환경에서는 Transformer 계열 (예: BERT, GPT) 모델이 성능이나 툴링 면에서 성숙해 널리 쓰이고 있다. Mamba는 매우 유망한 기술이지만 아직 **라이브러리 지원, 커뮤니티, 사전학습 모델 풀**이 Transformer만큼 풍부하지 않다. 따라서 현업에서 바로 Mamba를 대체로 도입하기엔 안정성 검증이 더 필요할 수 있다. 다만, **메모리 용량 한계나 지연 시간 문제로 초장문맥 처리가 어려웠던 서비스**라면, 향후 Mamba 같은 모델을 도입해 돌파구를 마련할 수 있을 것이다. 예컨대 **긴 법률 문서 분석 서비스**나 **장기간 대화 히스토리를 유지해야 하는 챗봇** 등에서는, Mamba 아키텍처가 게임 체인저가 될 가능성이 있다.

또한 추후 등장하는 하이브리드 모델 (예: **Jamba: Transformer+Mamba 혼합 전문가**)이나 다른 선형 시퀀스 모델들과의 경쟁도 주목할 필요가 있다. 현재로선 **Transformer의 범용성 vs. Mamba의 특수성** 구도로 볼 수 있으며, 실제 프로덕션에서는 두 접근을 **상호보완적으로 활용**하는 방안도 고려된다. 예를 들어, 일반 대화는 Transformer로 처리하다가, 특정 요청에서 초장문맥 처리가 필요하면 Mamba 모드로 전환하는 식의 시스템도 가능할 것이다.

정리하면, **BERT**와 **Mamba**는 각자 강점을 가지며 사용 용도가 갈린다. **짧은 입력/기존 작업**에는 숙성된 BERT 계열이 적합하고, **긴 입력/새로운 확장 작업**에는 Mamba가 잠재력을 보인다. 연구와 기술 발전이 지속된다면 Mamba 같은 SSM이 Transformer의 한계를 보완하거나 대체하는 사례가 점차 늘어날 것으로 기대된다. 실제 서비스에 적용할 때는 현재 모델의 안정성, 지원 도구, 라이선스 등을 종합 고려해야 하지만, **미래 지향적으로는 초장문맥과 고효율 추론을 위한 아키텍처 혁신이 현실화되고 있다**는 점에서 이 두 모델의 비교 실험은 의미 있는 통찰을 제공한다.

---

## 참고자료

- PyTorch Autograd 공식 문서 – _"Autograd: Automatic Differentiation"_
- Tri Dao 블로그 – _"FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision"_
- Hugging Face Transformers Documentation & Tutorials
- Databricks DSPy 소개 – _Programming, not prompting_
- Deepset Haystack 문서 – _Flexible Open Source QA Framework_
- CrewAI Docs – _Role-based Autonomous Agent Teams_
- Mamba 아키텍처 논문 – _Mamba: A Linear-Time State Space Model for Long-Range Sequences_
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
