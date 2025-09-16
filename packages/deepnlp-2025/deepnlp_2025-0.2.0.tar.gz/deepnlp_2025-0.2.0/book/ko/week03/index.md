# Week 3: 현대적 PEFT 기법을 활용한 효율적 파인튜닝

## 서론: 왜 파라미터 효율적 파인튜닝인가?

지난 주차들에서 PyTorch와 Hugging Face를 사용하여 사전학습된 모델을 로드하고 NLP 작업에 대한 기본적인 파인튜닝을 수행하는 방법을 배웠다. 하지만 GPT, BERT, LLaMA와 같은 대형 언어모델(LLM)을 완전 파인튜닝하는 것은 다음과 같은 중요한 도전과제들을 제시한다:

- **메모리 요구사항**: 7B 파라미터 모델을 파인튜닝하려면 모델 가중치만으로도 ~28GB의 GPU 메모리가 필요하며, 그래디언트와 옵티마이저 상태를 위한 추가 메모리도 필요하다
- **계산 비용**: 수십억 개의 파라미터를 업데이트하는 것은 계산적으로 비용이 많이 들고 시간이 오래 걸린다
- **과적합 위험**: 제한된 훈련 데이터로 완전 파인튜닝을 수행하면 사전학습된 지식의 파괴적 망각(catastrophic forgetting)이 발생할 수 있다
- **저장 오버헤드**: 각 파인튜닝된 모델은 모든 파라미터를 저장해야 하므로, 여러 작업별 모델을 유지하는 것이 비현실적이다

**파라미터 효율적 파인튜닝(Parameter-Efficient Fine-Tuning, PEFT)**은 나머지 부분을 고정된 상태로 유지하면서 모델 파라미터의 작은 부분만 훈련함으로써 이러한 도전과제들을 해결한다. 이 접근법은 메모리 사용량을 90% 이상 줄이고 훈련 시간을 10배 단축할 수 있으며, 종종 완전 파인튜닝과 비교할 만하거나 더 우수한 성능을 달성한다.

### PEFT의 주요 장점

- **메모리 효율성**: 단일 48GB GPU에서 65B 파라미터 모델을 훈련할 수 있다 (완전 파인튜닝으로는 불가능)
- **빠른 훈련**: 적은 파라미터는 더 빠른 그래디언트 계산과 수렴을 의미한다
- **더 나은 일반화**: 제한된 파라미터 업데이트는 작은 데이터셋에서의 과적합을 줄인다
- **모듈성**: 작은 어댑터 모듈을 쉽게 저장, 공유, 교체할 수 있다
- **추론 오버헤드 없음**: 어댑터를 배포를 위해 기본 가중치로 다시 병합할 수 있다

이번 강의에서는 효율성을 더욱 끌어올리는 최첨단 PEFT 기법들을 탐구할 것이다: **WaveFT**, **DoRA**, **VB-LoRA**, **QR-Adaptor**, **QLoRA**. 이러한 방법들은 효율적 파인튜닝의 최신 기술을 나타내며, 연구자와 실무자들이 최소한의 계산 자원으로 대형 모델을 적응시킬 수 있게 해준다.

## 현대적 PEFT 기법의 개념적 개요

### **1. 복습: 저차원 적응(Low-Rank Adaptation, LoRA)**

고급 PEFT 방법들을 탐구하기 전에, 많은 현대적 기법들의 기초가 되는 LoRA(저차원 적응)를 복습해보자.

#### 핵심 개념

LoRA는 **파인튜닝 중 가중치 업데이트가 저차원 부분공간에 놓여있다**는 핵심 통찰에 기반한다. 전체 가중치 행렬 $W_0 \in \mathbb{R}^{d \times k}$를 업데이트하는 대신, LoRA는 업데이트를 다음과 같이 분해한다:

$$\Delta W = A \times B$$

여기서:
- $A \in \mathbb{R}^{d \times r}$와 $B \in \mathbb{R}^{r \times k}$는 저차원 행렬이다
- $r \ll \min(d, k)$는 랭크이다 (일반적으로 4, 8, 또는 16)
- $A$와 $B$만 훈련 가능한 파라미터이다

최종 가중치는 다음과 같다: $W = W_0 + \Delta W = W_0 + AB$

#### 주요 장점

- **파라미터 효율성**: $d \times k$ 가중치 행렬에 대해 LoRA는 $dk$ 대신 $r(d + k)$ 파라미터만 사용한다
- **메모리 감소**: 일반적으로 원본 파라미터의 0.1%-0.5%
- **추론 오버헤드 없음**: 훈련 후 $\Delta W$를 $W_0$에 병합할 수 있다
- **모듈성**: 어댑터를 다른 작업에 맞게 교체할 수 있다

#### 수학적 예시

랭크 $r=8$인 768×768 어텐션 가중치 행렬의 경우:
- 완전 파인튜닝: 768² = 589,824 파라미터
- LoRA: 8×(768+768) = 12,288 파라미터 (98% 감소!)

#### 한계

LoRA의 주요 한계는 **"저차원 병목"**이다 - 랭크-$r$ 행렬로 업데이트를 제한하는 것은 매우 적은 파라미터가 사용 가능할 때 표현력을 제한할 수 있다. 이는 우리가 다음에 탐구할 고급 방법들의 동기가 된다.

### 체크포인트 질문

- LoRA가 가중치 업데이트가 저차원 부분공간에 놓여있다고 가정하는 이유는 무엇인가?
- LoRA 랭크 $r=16$으로 1024×1024 가중치 행렬의 파라미터 감소를 계산하라
- LoRA 어댑터를 사용할 때 추론 속도에 어떤 일이 일어나는가?

### **2. 웨이블릿 파인튜닝(Wavelet Fine-Tuning, WaveFT)**

WaveFT(2025)는 표준 파라미터 공간이 아닌 **웨이블릿 도메인**에서 모델을 파인튜닝함으로써 패러다임 전환을 나타낸다. 이 접근법은 웨이블릿의 다중 스케일 표현 능력을 활용하여 극도의 파라미터 효율성을 달성한다.

#### 핵심 개념

가중치 행렬을 직접 업데이트하는 대신, WaveFT는 다음과 같이 동작한다:

1. **변환**: 2D 웨이블릿 변환을 사용하여 가중치 행렬 $W_0$를 웨이블릿 계수로 변환한다
2. **선택**: 훈련 가능한 계수의 희소 부분집합을 선택한다 (예: 모든 계수의 0.01%)
3. **훈련**: 다른 계수들을 0으로 유지하면서 선택된 계수만 훈련한다
4. **재구성**: 역 웨이블릿 변환을 통해 가중치 업데이트 $\Delta W$를 재구성한다
5. **적용**: 업데이트를 적용한다: $W = W_0 + \Delta W$

#### 수학적 공식화

가중치 행렬 $W_0 \in \mathbb{R}^{d \times k}$에 대해:

1. **순방향 변환**: $C = \text{DWT}(W_0)$ (여기서 DWT는 2D 이산 웨이블릿 변환)
2. **희소 선택**: 계수의 부분집합 $S$를 선택하고 나머지는 마스킹: $C_{\text{train}} = C \odot M$
3. **훈련**: 그래디언트 하강을 통해 $C_{\text{train}}$만 업데이트
4. **역변환**: $\Delta W = \text{IDWT}(C_{\text{train}})$

#### 주요 장점

- **극도의 희소성**: 가중치 계수의 0.01%만 훈련할 수 있다
- **고차원 업데이트**: LoRA의 저차원 제약과 달리 WaveFT는 전체 랭크 업데이트를 생성할 수 있다
- **다중 스케일 학습**: 웨이블릿은 거친 패턴과 세밀한 패턴을 모두 포착한다
- **추론 오버헤드 없음**: 훈련 후 $\Delta W$가 $W_0$에 병합된다

#### 웨이블릿이 효과적인 이유

웨이블릿은 JPEG 압축이 작동하는 방식과 유사하게 신호를 여러 주파수 성분으로 분해한다. 이 다중 스케일 표현은 모델이 다음을 가능하게 한다:
- 넓은 저주파 패턴 조정 (전역적 변화)
- 고주파 세부사항 미세 조정 (국소적 조정)
- 가중치 공간에서의 계층적 의존성 포착

#### 성능 결과

WaveFT는 극도의 저파라미터 영역에서 놀라운 결과를 보여주었다:
- **Stable Diffusion**: LoRA보다 10배 적은 파라미터로 더 나은 주제 충실도와 이미지 다양성
- **언어 모델**: LoRA 파라미터 수의 0.1%로 경쟁력 있는 성능
- **메모리 효율성**: 수백만 개 대신 수천 개의 파라미터만으로 모델을 훈련할 수 있다

### 체크포인트 질문

- 가중치 업데이트의 수학적 구조 측면에서 WaveFT는 LoRA와 어떻게 다른가?
- 특정 유형의 가중치 패턴에 대해 웨이블릿 변환이 저차원 분해보다 더 효과적일 수 있는 이유는 무엇인가?
- WaveFT의 극도 희소성과 LoRA의 저차원 접근법 사이의 트레이드오프는 무엇인가?

### **3. 가중치 분해 저차원 적응(Weight-Decomposed Low-Rank Adaptation, DoRA)**

DoRA(NVIDIA, 2024)는 가중치 업데이트의 **크기(magnitude)**와 **방향(direction)** 성분을 명시적으로 분리함으로써 LoRA의 주요 한계를 해결한다. 이 분해는 더 큰 유연성을 제공하며 종종 표준 LoRA보다 우수한 성능을 달성한다.

#### 핵심 개념

DoRA는 각 가중치 행렬 $W_0$를 두 성분으로 분해한다:

1. **방향**: $V = \frac{W_0}{||W_0||}$ (정규화된 가중치 행렬)
2. **크기**: $m = ||W_0||$ (스칼라 또는 노름 벡터)

핵심 통찰은 이러한 성분들이 파인튜닝 중에 **독립적으로** 업데이트될 수 있다는 것이다.

#### 수학적 공식화

가중치 행렬 $W_0 \in \mathbb{R}^{d \times k}$에 대해:

1. **분해**: 
   - $V = \frac{W_0}{||W_0||_F}$ (프로베니우스 노름 정규화)
   - $m = ||W_0||_F$ (크기 스칼라)

2. **방향 업데이트**: 방향에 LoRA 적용
   - $\Delta V = AB$ (여기서 $A \in \mathbb{R}^{d \times r}$, $B \in \mathbb{R}^{r \times k}$)
   - $V' = V + \Delta V$

3. **크기 업데이트**: 스케일링 인수 학습
   - $m' = m + \Delta m$ (여기서 $\Delta m$은 학습 가능한 스칼라)

4. **재구성**: $W' = m' \times \frac{V'}{||V'||_F}$

![DoRA Architecture](figs/image1.jpeg)
*DoRA의 설명: 사전학습된 가중치 $W_0$는 고정된 방향 $V$와 학습 가능한 크기 $m$으로 분해된다. DoRA는 방향을 조정하기 위해 LoRA 스타일의 저차원 업데이트(랭크 $r$의 행렬 $A$, $B$)를 적용하고($V + \Delta V$ 생성) 크기 $m$도 조정한다. 훈련 후, 크기와 새로운 방향이 곱해져 병합된 가중치 $W'$를 형성한다. 파란색 성분은 고정되고, 녹색은 훈련 가능하다 (DoRA 논문에서 적응).*

#### 주요 장점

- **분리된 업데이트**: 크기와 방향이 독립적으로 변경될 수 있다
- **더 나은 표현력**: 스케일링과 방향적 변화를 모두 포착한다
- **최소 오버헤드**: 레이어당 몇 개의 크기 파라미터만 추가한다
- **드롭인 대체**: LoRA가 적용되는 모든 곳에서 사용할 수 있다

#### 작동 원리

전통적인 LoRA 업데이트는 저차원 구조에 의해 제약받아, 모델이 특정 유형의 가중치 조정을 수행하는 능력을 제한할 수 있다. DoRA는 다음을 통해 이를 해결한다:

- **크기 제어**: 모델이 가중치를 전역적으로 확대하거나 축소할 수 있게 한다
- **방향 유연성**: LoRA를 통한 세밀한 방향적 조정을 가능하게 한다
- **독립적 학습**: 크기와 방향 업데이트가 서로 간섭하지 않는다

#### 성능 결과

DoRA는 다양한 벤치마크에서 LoRA를 지속적으로 능가한다:

- **LLaMA-7B**: 상식 추론 작업에서 평균 3.7% 개선
- **파라미터 효율성**: 25% 적은 훈련 가능한 파라미터로 더 나은 결과 달성
- **저차원 설정**: LoRA 랭크가 제약될 때 특히 효과적
- **훈련 역학**: 가중치 업데이트 패턴이 완전 파인튜닝과 더 유사하다

#### 구현 고려사항

DoRA는 최소한의 계산 오버헤드를 추가한다:
- **메모리**: 적응된 레이어당 몇 개의 추가 스칼라만
- **훈련**: 약간 더 복잡한 그래디언트 계산
- **추론**: 병합 후 오버헤드 없음 (LoRA와 동일)

### 체크포인트 질문

- DoRA의 가중치 분해는 LoRA의 저차원 근사와 어떻게 다른가?
- 크기와 방향 업데이트를 분리하는 것이 더 나은 성능으로 이어질 수 있는 이유는 무엇인가?
- LoRA 대신 DoRA를 사용할 때의 계산적 트레이드오프는 무엇인가?

### **4. VB-LoRA (벡터 뱅크 LoRA)**

VB-LoRA(2023)는 모든 레이어에 걸친 **전역 파라미터 공유**를 도입하여 파라미터 효율성을 극한까지 끌어올린다. 각 레이어에 대해 별도의 LoRA 행렬을 학습하는 대신, VB-LoRA는 모든 레이어가 접근할 수 있는 공유 "벡터 뱅크"를 유지한다.

#### 핵심 개념

VB-LoRA는 서로 다른 레이어들이 종종 **유사한 유형의 업데이트**가 필요하다는 원리에 따라 동작한다. 각 레이어에 대해 독립적인 $A$와 $B$ 행렬을 학습하는 대신, 다음과 같이 동작한다:

1. **유지**: 재사용 가능한 벡터들의 전역 벡터 뱅크 $\mathcal{B} = \{v_1, v_2, ..., v_N\}$를 유지한다
2. **구성**: 이 뱅크에서 선택된 벡터들로 각 레이어의 LoRA 행렬을 구성한다
3. **학습**: 각 레이어에 대한 선택 가중치와 혼합 계수를 학습한다

#### 수학적 공식화

LoRA 행렬 $A_l$과 $B_l$을 가진 레이어 $l$에 대해:

1. **벡터 선택**: 뱅크 $\mathcal{B}$에서 상위 $k$개 벡터 선택
   - $S_l = \text{TopK}(\text{similarity}(A_l, \mathcal{B}), k)$

2. **행렬 구성**: 
   - $A_l = \sum_{i \in S_l} w_{l,i} \cdot v_i \cdot U_{l,i}$
   - $B_l = \sum_{i \in S_l} w'_{l,i} \cdot v_i \cdot V_{l,i}$

3. **파라미터 공유**: $w_{l,i}$, $w'_{l,i}$, $U_{l,i}$, $V_{l,i}$만 레이어별로 특화된다

#### 주요 장점

- **극도의 압축**: 표준 LoRA 대비 어댑터 크기를 100배까지 줄일 수 있다
- **전역 협력**: 레이어들이 학습된 패턴과 표현을 공유할 수 있다
- **확장성**: 파라미터 수가 모델 깊이에 선형적으로 증가하지 않는다
- **저장 효율성**: 여러 작업별 어댑터 배포에 이상적이다

#### 성능 결과

VB-LoRA는 성능 손실 없이 놀라운 압축을 달성한다:

- **LLaMA2-13B**: 표준 LoRA 파라미터의 0.4%, 더 나은 성능
- **저장**: 300MB → 2.5MB 어댑터 파일 (120배 압축)
- **다중 작업**: 하나의 표준 LoRA 공간에 100개 이상의 어댑터 저장 가능
- **엣지 배포**: 자원 제약이 있는 기기에서 파인튜닝된 모델 실행 가능

#### 구현 세부사항

벡터 뱅크 접근법은 다음을 통해 작동한다:

- **미분 가능한 선택**: 상위 $k$ 선택이 종단간 훈련을 위해 미분 가능하게 만들어진다
- **적응적 혼합**: 각 레이어가 선택된 벡터를 최적으로 결합하는 방법을 학습한다
- **계층적 공유**: 서로 다른 레이어가 뱅크의 서로 다른 부분집합에 접근할 수 있다

#### 사용 사례

VB-LoRA는 다음에 특히 가치가 있다:

- **다중 작업 학습**: 많은 서로 다른 작업에 대한 모델 훈련
- **엣지 배포**: 모바일/임베디드 기기에서 파인튜닝된 모델 실행
- **모델 공유**: 작업별 어댑터를 효율적으로 배포
- **자원 제약 환경**: 저장 공간과 메모리가 제한된 곳

### 체크포인트 질문

- VB-LoRA의 파라미터 공유는 표준 LoRA의 레이어별 접근법과 어떻게 다른가?
- 전역 파라미터 공유와 레이어별 적응 사이의 트레이드오프는 무엇인가?
- VB-LoRA가 다중 작업 학습 시나리오에 특히 유용할 수 있는 이유는 무엇인가?

### **5. QR-Adaptor (적응적 랭크 및 양자화)**

QR-Adaptor(2025)는 각 레이어에 대해 **양자화 정밀도와 어댑터 랭크를 공동으로 최적화**함으로써 패러다임 전환을 나타낸다. 양자화와 적응을 별도로 처리하는 이전 방법들과 달리, QR-Adaptor는 메모리 제약 하에서 성능을 최대화하기 위해 비트 폭과 LoRA 랭크의 최적 조합을 찾는다.

#### 핵심 개념

QR-Adaptor는 **서로 다른 레이어가 양자화와 적응에 대해 서로 다른 민감도**를 가진다는 핵심 통찰을 다룬다:

- **중요한 레이어** (예: 어텐션 메커니즘)는 더 높은 정밀도와 더 큰 어댑터가 필요할 수 있다
- **덜 민감한 레이어** (예: 일부 피드포워드 구성요소)는 최소한의 어댑터로 강하게 양자화될 수 있다
- **메모리 예산의 최적 할당**이 균일한 접근법을 능가할 수 있다

#### 수학적 공식화

각 레이어 $l$에 대해 QR-Adaptor는 다음을 최적화한다:

$$\min_{\{b_l, r_l\}} \mathcal{L}_{\text{task}}(f(\{b_l, r_l\})) \quad \text{s.t.} \quad \sum_l \text{Memory}(b_l, r_l) \leq B$$

여기서:
- $b_l \in \{4, 8, 16\}$는 레이어 $l$의 비트 폭이다
- $r_l \in \{0, 2, 4, 8, 16\}$는 레이어 $l$의 LoRA 랭크이다
- $B$는 총 메모리 예산이다
- $\mathcal{L}_{\text{task}}$는 작업별 손실이다

#### 최적화 전략

QR-Adaptor는 **그래디언트 없는 검색** 접근법을 사용한다:

1. **보정**: 작은 검증 세트에서 서로 다른 구성을 평가한다
2. **검색**: 진화 알고리즘이나 베이지안 최적화를 사용하여 최적 할당을 찾는다
3. **검증**: 전체 훈련 세트에서 최고 구성을 테스트한다

#### 주요 장점

- **레이어별 적응성**: 각 레이어가 최적의 정밀도와 랭크 할당을 받는다
- **성능 우선**: 양자화 오차뿐만 아니라 작업 성능을 직접 최적화한다
- **메모리 효율성**: 동일한 메모리 예산으로 더 나은 결과를 달성한다
- **자동화**: 레이어별 양자화/랭크의 수동 튜닝이 필요 없다

#### 성능 결과

QR-Adaptor는 놀라운 개선을 달성한다:

- **GSM8K**: 고정 정밀도 접근법 대비 4.9% 정확도 개선
- **메모리 효율성**: 16비트 완전 파인튜닝을 능가하는 4비트 모델
- **레이어 할당**: 중요한 레이어는 8비트 정밀도, 나머지는 4비트 사용
- **랭크 최적화**: 어텐션 레이어는 랭크-16, 나머지는 랭크-4 또는 어댑터 없음

#### 예시 구성

일반적인 QR-Adaptor 구성은 다음과 같을 수 있다:

- **레이어 1-6** (임베딩): 4비트, LoRA 없음
- **레이어 7-12** (어텐션): 8비트, 랭크-16 LoRA
- **레이어 13-18** (피드포워드): 4비트, 랭크-4 LoRA
- **레이어 19-24** (출력): 8비트, 랭크-8 LoRA

#### 구현 고려사항

QR-Adaptor는 다음을 요구한다:

- **검색 시간**: 초기 구성 검색에 추가 시간이 필요하다
- **보정 데이터**: 구성 평가를 위한 대표적인 데이터가 필요하다
- **하드웨어 지원**: 혼합 정밀도 훈련 기능이 필요하다

#### 사용 시기

QR-Adaptor는 다음에 이상적이다:

- **메모리 제약 배포**: 성능의 모든 비트가 중요할 때
- **프로덕션 시스템**: 최적의 자원 할당이 중요한 곳
- **연구**: 양자화에 대한 레이어별 민감도 이해
- **자동화된 최적화**: 수동 튜닝이 비현실적일 때

### 체크포인트 질문

- QR-Adaptor의 레이어별 최적화는 균일한 양자화 접근법과 어떻게 다른가?
- 서로 다른 레이어가 서로 다른 정밀도와 랭크 할당을 요구할 수 있는 이유는 무엇인가?
- QR-Adaptor의 검색 복잡성과 성능 향상 사이의 트레이드오프는 무엇인가?

### **6. QLoRA와 4비트 NF4 양자화**

QLoRA(Quantized LoRA)는 효율적 파인튜닝의 돌파구를 나타내며, 단일 48GB GPU에서 65B 파라미터 모델의 훈련을 가능하게 한다. 핵심 혁신은 성능을 유지하면서 4비트 양자화와 LoRA 어댑터를 결합하는 데 있다.

#### 핵심 개념

QLoRA는 3단계 접근법을 따른다:

1. **양자화**: 사전학습된 모델 가중치를 4비트 정밀도로 양자화한다
2. **고정**: 양자화된 가중치를 고정한다 (그래디언트 업데이트 없음)
3. **훈련**: 양자화된 가중치를 통한 완전한 역전파로 16비트 정밀도에서 LoRA 어댑터를 훈련한다

이 조합은 모델 성능을 보존하면서 메모리 사용량을 ~75% 줄인다.

#### NF4 양자화: 핵심 혁신

QLoRA의 성공은 신경망 가중치에 최적화된 사용자 정의 4비트 데이터 타입인 **NF4(NormalFloat-4)**에 달려있다:

- **정보 이론적으로 최적**: NF4는 신경 가중치의 정규 분포와 일치하는 로그 분포를 사용한다
- **우수한 성능**: 표준 4비트 양자화 대비 27.4 vs 31.1 perplexity를 달성한다
- **효율적인 표현**: 가중치 분포에 걸쳐 16개의 가능한 4비트 값을 최적으로 사용한다

#### 기술적 혁신

**이중 양자화:**
- 모델 가중치(4비트)와 스케일링 인수(8비트) 모두를 양자화한다
- 성능 손실 없이 메모리 오버헤드를 더욱 줄인다
- bitsandbytes 라이브러리에서 효율적으로 구현된다

**페이징된 옵티마이저:**
- 피크 시 그래디언트와 모멘텀을 CPU 메모리로 스왑한다
- 대형 모델에서 메모리 부족 오류를 방지한다
- 그렇지 않으면 맞지 않을 모델의 훈련을 가능하게 한다

#### 성능 결과

QLoRA는 놀라운 결과를 달성한다:

- **메모리 효율성**: 메모리 사용량 75% 감소
- **성능 동등성**: GLUE와 지시 따르기 작업에서 완전 16비트 파인튜닝과 일치
- **확장성**: 단일 GPU에서 30B-65B 모델의 파인튜닝 가능
- **속도**: 현대 하드웨어에서 4비트 연산이 종종 16비트보다 빠르다

![QLoRA Comparison](figs/image3.jpeg)
*완전 파인튜닝 vs LoRA vs QLoRA 비교 (개념적). 왼쪽: 완전 파인튜닝은 모든 모델 가중치를 업데이트(16비트 정밀도)하고 큰 옵티마이저 상태(가중치당 32비트)를 저장해야 한다. 가운데: LoRA 파인튜닝은 기본 가중치를 16비트로 유지하고 고정하며, 작은 16비트 어댑터 행렬을 훈련한다(업데이트할 것이 훨씬 적음; 옵티마이저는 그것들만). 오른쪽: QLoRA는 동일한 저차원 적응을 수행하지만 4비트 양자화된 기본 모델에서; 그래디언트(녹색 화살표)가 4비트 모델을 통해 LoRA 어댑터로 흐른다. 자홍색 화살표는 QLoRA의 페이징된 옵티마이저가 상태를 CPU로 오프로드함을 나타낸다. 이 접근법은 성능을 보존하면서 메모리를 ~75% 절약한다.*

#### 실제 구현

```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

# 4비트 양자화 구성
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# 양자화로 모델 로드
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=quantization_config,
    device_map="auto"
)

# LoRA 적용
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.1
)

model = get_peft_model(model, lora_config)
```

#### QLoRA 사용 시기

QLoRA는 다음에 이상적이다:

- **대형 모델**: 메모리가 제약인 7B+ 파라미터 모델
- **자원 제한 환경**: 제한된 메모리를 가진 단일 GPU 설정
- **연구**: 대형 모델로 실험해야 할 때
- **프로덕션**: 메모리 효율성이 중요할 때

#### 한계

- **하드웨어 요구사항**: 4비트 지원 GPU가 필요하다
- **설정 복잡성**: 표준 파인튜닝보다 더 복잡하다
- **라이브러리 의존성**: bitsandbytes와 호환 가능한 transformers가 필요하다

### 체크포인트 질문

- NF4 양자화는 표준 4비트 양자화 접근법과 어떻게 다른가?
- QLoRA가 효과적으로 작동하게 하는 핵심 기술적 혁신은 무엇인가?
- 표준 LoRA나 완전 파인튜닝 대신 QLoRA를 선택할 때는 언제인가?

---

## 실제 응용: PEFT 방법 구현 및 비교

이제 이론적 기초를 이해했으니, 이러한 기법들을 실제로 어떻게 구현하는지 탐구해보자. PyTorch와 Hugging Face 라이브러리를 사용한 실습 예제에 집중할 것이다.

### **1. 기본 LoRA 구현**

한국어 감성 분석을 위한 완전한 LoRA 구현으로 시작해보자:

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

# 한국어 BERT 모델 로드
model_name = "klue/bert-base"
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=2,
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# LoRA 구성
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,                    # LoRA 랭크
    lora_alpha=32,          # 스케일링 인수
    target_modules=["query", "value", "key", "dense"],  # 대상 어텐션 및 FFN 레이어
    lora_dropout=0.1,
    bias="none"
)

# 모델에 LoRA 적용
model = get_peft_model(model, lora_config)
print(f"Trainable parameters: {model.print_trainable_parameters()}")

# 한국어 감성 데이터 준비 (예시)
def prepare_dataset():
    texts = [
        "이 영화 정말 재밌어요!",
        "너무 지루하고 별로예요.",
        "배우들의 연기가 훌륭해요.",
        "스토리가 너무 복잡해요."
    ]
    labels = [1, 0, 1, 0]  # 1: 긍정, 0: 부정
    
    # 토큰화
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

# 훈련 설정
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

# 모델 훈련
trainer.train()

# LoRA 어댑터 저장
model.save_pretrained("./lora_adapter")
```

### **2. QLoRA 구현**

더 큰 모델에 대한 QLoRA 구현 방법은 다음과 같다:

```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
import torch

# 4비트 양자화 구성
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# 양자화로 모델 로드
model = AutoModelForCausalLM.from_pretrained(
    "beomi/KoAlpaca-7B",
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# QLoRA를 위한 LoRA 구성
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

# LoRA 적용
model = get_peft_model(model, lora_config)

# QLoRA로 훈련
training_args = TrainingArguments(
    output_dir="./qlorafinetuned",
    num_train_epochs=3,
    per_device_train_batch_size=1,  # 메모리 제약으로 인한 더 작은 배치 크기
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    remove_unused_columns=False,
)

# QLoRA로 Trainer 사용
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()
```

### **3. DoRA 구현**

DoRA가 아직 메인 PEFT 라이브러리에 포함되지 않았지만, 개념적 구현은 다음과 같다:

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
        
        # LoRA 행렬
        self.lora_A = nn.Linear(base_layer.in_features, rank, bias=False)
        self.lora_B = nn.Linear(rank, base_layer.out_features, bias=False)
        
        # 크기 파라미터
        self.magnitude = nn.Parameter(torch.ones(base_layer.out_features))
        
        # 초기화
        nn.init.kaiming_uniform_(self.lora_A.weight)
        nn.init.zeros_(self.lora_B.weight)
        
    def forward(self, x):
        # 기본 출력 얻기
        base_output = self.base_layer(x)
        
        # LoRA 업데이트
        lora_output = self.lora_B(self.lora_A(x)) * (self.alpha / self.rank)
        
        # 크기 스케일링 적용
        scaled_output = (base_output + lora_output) * self.magnitude
        
        return scaled_output

# 사용 예시
def apply_dora_to_model(model, target_modules, rank=8, alpha=32):
    for name, module in model.named_modules():
        if any(target in name for target in target_modules):
            if isinstance(module, nn.Linear):
                # DoRA 레이어로 교체
                dora_layer = DoRALayer(module, rank=rank, alpha=alpha)
                # 모델 구조 업데이트
                parent_name = '.'.join(name.split('.')[:-1])
                child_name = name.split('.')[-1]
                parent_module = model.get_submodule(parent_name)
                setattr(parent_module, child_name, dora_layer)
    
    return model
```

### **4. 비교 프레임워크**

서로 다른 PEFT 방법들을 비교하기 위한 프레임워크는 다음과 같다:

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
        """PEFT 방법을 평가하고 메트릭을 기록한다"""
        
        # 모델 로드
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, num_labels=2
        )
        
        # PEFT 방법 적용
        if method_name == "LoRA":
            peft_config = LoraConfig(**config)
            model = get_peft_model(model, peft_config)
        elif method_name == "DoRA":
            model = apply_dora_to_model(model, **config)
        # 다른 방법들 추가...
        
        # 메트릭 기록
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 훈련 (간소화)
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
        
        # 결과 기록
        self.results[method_name] = {
            "trainable_params": sum(p.numel() for p in model.parameters() if p.requires_grad),
            "total_params": sum(p.numel() for p in model.parameters()),
            "training_time": end_time - start_time,
            "memory_usage": end_memory - start_memory,
            "config": config
        }
        
        return self.results[method_name]
    
    def compare_methods(self):
        """모든 방법을 비교하고 결과를 출력한다"""
        print("PEFT 방법 비교")
        print("=" * 50)
        
        for method, results in self.results.items():
            print(f"\n{method}:")
            print(f"  훈련 가능한 파라미터: {results['trainable_params']:,}")
            print(f"  파라미터 비율: {results['trainable_params']/results['total_params']:.4f}")
            print(f"  훈련 시간: {results['training_time']:.2f}초")
            print(f"  메모리 사용량: {results['memory_usage']:.2f}MB")

# 사용법
comparison = PEFTComparison("klue/bert-base", train_dataset)

# 서로 다른 방법들 비교
comparison.evaluate_method("LoRA", {"r": 8, "lora_alpha": 32})
comparison.evaluate_method("DoRA", {"target_modules": ["query", "value"], "rank": 8})
# 더 많은 방법들 추가...

comparison.compare_methods()
```

### **5. 모범 사례 및 팁**

**올바른 방법 선택:**

- **작은 데이터셋 (< 1K 예시)**: 극도의 효율성을 위해 WaveFT 또는 VB-LoRA 사용
- **중간 데이터셋 (1K-10K 예시)**: LoRA보다 더 나은 성능을 위해 DoRA 사용
- **큰 데이터셋 (> 10K 예시)**: 메모리 효율성을 위해 QLoRA 사용
- **다중 작업**: 저장 효율성을 위해 VB-LoRA 사용

**하이퍼파라미터 튜닝:**

```python
# LoRA 하이퍼파라미터
lora_configs = [
    {"r": 4, "lora_alpha": 16},   # 최소 파라미터
    {"r": 8, "lora_alpha": 32},   # 균형
    {"r": 16, "lora_alpha": 64},  # 높은 용량
]

# 대상 모듈 선택
target_modules_options = [
    ["query", "value"],                    # 어텐션만
    ["query", "value", "key"],             # 전체 어텐션
    ["query", "value", "key", "dense"],    # 어텐션 + FFN
]
```

**메모리 최적화:**

```python
# 그래디언트 체크포인팅 활성화
training_args = TrainingArguments(
    gradient_checkpointing=True,
    dataloader_pin_memory=False,
    dataloader_num_workers=0,
)

# 혼합 정밀도 사용
training_args = TrainingArguments(
    fp16=True,  # 또는 더 새로운 GPU의 경우 bf16=True
)
```

### 체크포인트 질문

- 특정 작업에 대해 LoRA와 DoRA 중 어떻게 선택하겠는가?
- QLoRA를 구현할 때 주요 고려사항은 무엇인가?
- PEFT 방법들을 공정하게 비교하는 실험을 어떻게 설계하겠는가?

## 요약 및 미래 방향

이번 강의에서 우리는 파라미터 효율적 파인튜닝(PEFT) 기법의 최첨단 풍경을 탐구했다. 주요 내용을 요약하고 미래 발전을 살펴보자.

### **방법 비교 요약**

| 방법 | 파라미터 효율성 | 성능 | 사용 사례 |
|------|----------------|------|----------|
| **LoRA** | 모델의 0.1-0.5% | 기준선 | 일반 목적 |
| **DoRA** | 모델의 0.1-0.5% | LoRA 대비 +3.7% | 더 나은 성능 필요 |
| **WaveFT** | 모델의 0.01-0.1% | 경쟁력 있음 | 극도의 효율성 |
| **VB-LoRA** | LoRA의 0.01% | LoRA보다 나음 | 다중 작업 시나리오 |
| **QR-Adaptor** | 가변 | 고정 대비 +4.9% | 메모리 제약 |
| **QLoRA** | 75% 메모리 감소 | 완전 FT와 일치 | 대형 모델 |

### **핵심 통찰**

1. **파라미터 효율성 vs 성능 트레이드오프**: 극도의 효율성(WaveFT)에서 더 나은 성능(DoRA)까지 명확한 스펙트럼이 있어, 실무자들이 제약에 따라 선택할 수 있다.

2. **레이어별 최적화**: QR-Adaptor와 같은 방법들은 서로 다른 레이어가 양자화와 적응에 대해 서로 다른 민감도를 가진다는 것을 보여주며, 새로운 최적화 기회를 열어준다.

3. **전역 파라미터 공유**: VB-LoRA는 레이어 간 파라미터 공유가 성능을 유지하면서 저장 공간을 극적으로 줄일 수 있음을 보여준다.

4. **양자화 통합**: QLoRA는 4비트 양자화가 성능 손실 없이 PEFT와 결합될 수 있음을 증명하며, 훨씬 더 큰 모델의 훈련을 가능하게 한다.

### **올바른 방법 선택**

**연구 및 실험을 위해:**
- 기준 성능을 위해 LoRA로 시작
- 더 나은 결과가 필요할 때 DoRA 사용
- 극도의 파라미터 제약을 위해 WaveFT 시도

**프로덕션 배포를 위해:**
- 대형 모델(7B+ 파라미터)에 QLoRA 사용
- 메모리 제약 환경에 QR-Adaptor 고려
- 다중 작업 시나리오에 VB-LoRA 사용

**자원 제한 환경을 위해:**
- 최소 파라미터 예산에 WaveFT
- 메모리 제약에 QLoRA
- 저장 제한에 VB-LoRA

### **미래 방향**

PEFT 분야는 빠르게 진화하고 있다. 미래 발전의 주요 영역은 다음과 같다:

1. **자동화된 PEFT 선택**: 주어진 작업과 제약에 대해 최고의 PEFT 기법을 자동으로 선택하는 AI 기반 방법.

2. **동적 적응**: 작업 복잡성에 따라 훈련 중 파라미터 효율성을 조정할 수 있는 방법.

3. **크로스 모달 PEFT**: PEFT 기법을 멀티모달 모델(비전-언어, 오디오-텍스트)로 확장.

4. **하드웨어 인식 PEFT**: 서로 다른 하드웨어 구성(모바일, 엣지, 클라우드)에 특별히 최적화된 기법.

5. **연합 PEFT**: 서로 다른 클라이언트가 로컬 제약에 따라 서로 다른 PEFT 방법을 사용하는 분산 파인튜닝.

### **실용적 권장사항**

1. **간단하게 시작**: 대부분의 작업에 대해 LoRA로 시작한 다음, 필요에 따라 더 고급 방법을 탐구한다.

2. **제약 프로파일링**: 방법을 선택하기 전에 메모리, 계산, 저장 제한을 이해한다.

3. **체계적으로 실험**: 제공된 비교 프레임워크를 사용하여 특정 작업에서 서로 다른 방법을 평가한다.

4. **최신 상태 유지**: PEFT 분야는 빠르게 진화하고 있으며, 새로운 방법이 정기적으로 발표된다.

5. **전체 파이프라인 고려**: 훈련 효율성뿐만 아니라 배포, 저장, 추론 고려사항도 고려한다.

### **최종 생각**

PEFT 기법은 대형 언어모델 파인튜닝에 대한 접근을 민주화하여, 연구자와 실무자가 최소한의 계산 자원으로 강력한 모델을 적응시킬 수 있게 했다. 우리가 탐구한 방법들은 현재의 최신 기술을 나타내지만, 이 분야는 계속해서 빠르게 진화하고 있다.

PEFT에서 성공의 열쇠는 파라미터 효율성, 성능, 계산 요구사항 사이의 트레이드오프를 이해하는 것이다. 특정 사용 사례와 제약에 맞는 올바른 방법을 선택함으로써, 최소한의 자원으로 놀라운 결과를 달성할 수 있다.

앞으로 나아가면서, 성능을 유지하거나 개선하면서 효율성의 경계를 밀어붙이는 더욱 정교한 PEFT 기법을 볼 수 있을 것이다. 효율적 파인튜닝의 미래는 밝으며, 이러한 기법들은 대형 언어모델을 모든 사람에게 접근 가능하게 만드는 데 계속해서 중요한 역할을 할 것이다.

## 참고자료

1. **PEFT: LLM을 위한 파라미터 효율적 파인튜닝 방법**
   - [Hugging Face 블로그](https://huggingface.co/blog/samuellimabraz/peft-methods)

2. **웨이블릿을 사용한 파라미터 효율적 파인튜닝의 희소성 탐구**
   - [문헌 리뷰](https://www.themoonlight.io/en/review/exploring-sparsity-for-parameter-efficient-fine-tuning-using-wavelets)
   - [arXiv:2505.12532](https://arxiv.org/abs/2505.12532)

3. **DoRA: 가중치 분해 저차원 적응**
   - [arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
   - [NVIDIA 기술 블로그](https://developer.nvidia.com/blog/introducing-dora-a-high-performing-alternative-to-lora-for-fine-tuning/)

4. **VB-LoRA: 벡터 뱅크를 사용한 극도의 파라미터 효율적 파인튜닝**
   - [Hugging Face 문서](https://huggingface.co/docs/peft/en/package_reference/vblora)

5. **적응적 랭크와 비트폭을 통한 양자화된 모델의 효율적 파인튜닝**
   - [arXiv:2505.03802](https://arxiv.org/abs/2505.03802)

6. **bitsandbytes, 4비트 양자화 및 QLoRA로 LLM을 더욱 접근 가능하게 만들기**
   - [Hugging Face 블로그](https://huggingface.co/blog/4bit-transformers-bitsandbytes)
