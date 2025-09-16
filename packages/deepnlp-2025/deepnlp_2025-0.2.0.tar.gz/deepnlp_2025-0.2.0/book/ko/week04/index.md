# Week 4: 고급 프롬프트 기법과 최적화

## 1. 체계적 프롬프트 기법: 역할 부여와 구조화된 프롬프팅

대규모 언어모델(LLM)의 성능을 끌어올리기 위해 **프롬프트 엔지니어링** 기법들이 발전해왔다. 그 중 **역할 부여(role prompting)**와 **구조화된 프롬프팅(structured prompting)**은 모델의 응답 품질을 높이기 위한 체계적인 방법들이다.

### 1.1 역할 부여(Role Prompting)

**역할 부여**는 모델에게 특정 **페르소나**나 역할을 부여하여 답변 스타일과 초점을 조정하는 기법이다. 예를 들어 프롬프트를 "당신은 역사 선생님입니다. 산업혁명의 중요성을 설명하세요."와 같이 시작하면, 모델은 역사 교사의 어투와 관점을 모방하여 보다 맥락에 맞는 설명을 제공한다. 역할 부여를 통해 응답의 톤과 형식을 제어할 수 있을 뿐 아니라, 모델의 **추론 성능**도 향상될 수 있음이 보고되었다. 실제로 "당신은 수학자입니다…"와 같이 전문가 역할을 지정하면 복잡한 문제에서 모델이 **보다 일관되고 정확한 추론**을 하는 데 도움이 될 수 있다.

### 1.2 구조화된 프롬프팅(Structured Prompting)

**구조화된 프롬프팅**은 프롬프트를 명확한 **구조와 단계**에 따라 작성하여 모델이 체계적으로 답하도록 유도하는 기법이다. 단순 대화형 프롬프트와 달리, 구조화된 프롬프트는 역할, 과제, 형식 등을 명시적으로 구분한다. 예를 들어 **"역할(Role) - 과제(Task) - 형식(Format)"** 프레임워크를 사용하면:

- **Role**: "역사 선생님으로서,"
- **Task**: "1차 세계대전의 원인을 설명하고,"  
- **Format**: "학생이 이해하기 쉽게 bullet point로 답하세요."

이러한 **RTF 프레임워크** 외에도, **CIO (Context-Input-Output)**, **WWHW (Who-What-How-Why)** 등 여러 구조화 전략이 제안되어 왔다. 구조화된 프롬프트는 모델에게 **명확한 지침과 출력 형식**을 제공하므로, 응답의 **일관성**과 **정확성**을 높이는 데 효과적이다. 또한 JSON과 같은 포맷을 요구하는 **정형 출력**이 필요한 경우, 필드별로 프롬프트를 제시하여 신뢰성 있는 결과를 얻을 수 있다.

### 1.3 실습 예제: 체계적 프롬프트 구성

```python
def create_structured_prompt(role, task, format_instruction, context=""):
    """
    구조화된 프롬프트를 생성하는 함수
    
    Args:
        role: 모델에게 부여할 역할
        task: 수행할 과제
        format_instruction: 출력 형식 지시
        context: 추가 컨텍스트 (선택사항)
    """
    prompt = f"""역할(Role): {role}

과제(Task): {task}

형식(Format): {format_instruction}"""
    
    if context:
        prompt += f"\n\n컨텍스트: {context}"
    
    return prompt

# 예시 사용
role = "숙련된 소프트웨어 개발자"
task = "새로운 웹 서버를 설정하는 방법을 단계별로 알려주세요"
format_instruction = "각 단계를 번호로 나열하고, 중요한 부분은 강조해주세요"

prompt = create_structured_prompt(role, task, format_instruction)
print(prompt)
```

**출력 예시:**
```
역할(Role): 숙련된 소프트웨어 개발자

과제(Task): 새로운 웹 서버를 설정하는 방법을 단계별로 알려주세요

형식(Format): 각 단계를 번호로 나열하고, 중요한 부분은 강조해주세요
```

위와 같은 체계적 프롬프트는 모델이 답변할 **역할**과 **목표**, **형식**을 명확히 인지하도록 돕기 때문에, 산발적인 지시보다 높은 품질의 응답을 얻을 수 있다.

## 2. Self-Consistency 기법과 GSM8K 성능 향상

복잡한 문제에 대한 **체인-오브-생각(Chain-of-Thought, CoT)** 프롬프팅에서는 종종 모델이 한 번의 추론 경로만 따르기 때문에 **초기 경로의 편향**에 성능이 좌우될 수 있다. **Self-Consistency(자가 일관성)** 기법은 이러한 문제를 해결하기 위한 **디코딩 전략**으로, 한 번의 응답 대신 **다양한 추론 경로를 여러 번 샘플링**하고 최종 답을 **투표**로 결정한다. 다시 말해, 모델에게 동일한 질문에 대해 여러 **생각의 흐름**을 (주로 temperature를 주어) 생성하게 한 뒤, **가장 일관되게 등장하는 최종 답변**을 선택하는 방식이다.

이 방법의 직관은 "어려운 문제는 생각하는 경로는 다를 수 있어도 **정답은 하나**"라는 점을 활용하는 것이다. Self-Consistency를 적용하면 모델이 스스로 다양한 접근을 탐색한 후 **교집합에 가까운 답**을 취하게 되어, 단일 경로의 오류를 줄이고 복잡한 문제에서 성능을 크게 높일 수 있다.

### 2.1 GSM8K 성능 향상 사례

수학적 추론이 필요한 **GSM8K** 벤치마크에서 Self-Consistency는 매우 두드러진 향상을 보였다. Wang 등(2022)의 연구에 따르면, **CoT 프롬프트에 Self-Consistency 디코딩을 적용**했을 때 GSM8K에서 **기존 대비 17.9%p 성능 향상**을 달성했다. 예컨대, 한 모델의 GSM8K 정확도가 55%였던 것이 Self-Consistency 적용 후 약 72.9%로 상승한 셈이다. 이 기법은 다른 추론 과제들(SVAMP, AQuA, StrategyQA 등)에서도 두 자릿수의 성능 향상을 가져왔으며, ICLR 2023에 발표된 대표 논문에서도 해당 효과를 입증하였다.

### 2.2 Self-Consistency 구현 예제

```python
import openai
from collections import Counter
import re

def extract_final_answer(text):
    """텍스트에서 최종 답을 추출하는 함수"""
    # 다양한 패턴으로 답을 찾기
    patterns = [
        r'답은\s*(\d+)',
        r'정답은\s*(\d+)',
        r'따라서\s*(\d+)',
        r'결과는\s*(\d+)',
        r'(\d+)\s*입니다',
        r'(\d+)\s*이다'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # 마지막 숫자를 찾기
    numbers = re.findall(r'\d+', text)
    return numbers[-1] if numbers else None

def self_consistency_sampling(question, model="gpt-3.5-turbo", num_samples=5):
    """
    Self-Consistency를 통한 다중 샘플링 및 투표
    
    Args:
        question: 수학 문제
        model: 사용할 모델
        num_samples: 생성할 샘플 수
    """
    cot_prompt = f"""다음 수학 문제를 단계별로 풀어보세요.

문제: {question}

단계별로 생각해보고, 마지막에 최종 답을 제시하세요."""

    answers = []
    
    for i in range(num_samples):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": cot_prompt}],
                temperature=0.7,  # 다양성을 위해 높은 temperature 사용
                max_tokens=500
            )
            
            answer_text = response.choices[0].message.content
            final_answer = extract_final_answer(answer_text)
            
            if final_answer:
                answers.append(final_answer)
                print(f"샘플 {i+1}: {final_answer}")
            
        except Exception as e:
            print(f"샘플 {i+1} 생성 중 오류: {e}")
    
    # 투표를 통한 최종 답 결정
    if answers:
        answer_counts = Counter(answers)
        most_common = answer_counts.most_common(1)[0]
        final_answer = most_common[0]
        confidence = most_common[1] / len(answers)
        
        print(f"\n최종 답: {final_answer}")
        print(f"신뢰도: {confidence:.2f} ({most_common[1]}/{len(answers)})")
        
        return final_answer, confidence
    
    return None, 0

# 사용 예시
question = "사과 3개와 배 2개를 샀는데, 사과는 개당 500원, 배는 개당 700원입니다. 총 얼마를 지불해야 하나요?"

final_answer, confidence = self_consistency_sampling(question, num_samples=5)
```

**출력 예시:**
```
샘플 1: 2900
샘플 2: 2900
샘플 3: 2900
샘플 4: 2900
샘플 5: 2900

최종 답: 2900
신뢰도: 1.00 (5/5)
```

### 2.3 Self-Consistency의 장점과 한계

**장점:**
- **불확실성 감소**: 여러 경로를 탐색하여 단일 경로의 오류를 줄인다
- **안정적인 성능**: 수학 문제나 상식 추론 문제에서 더 안정적인 정답률을 제공한다
- **구현 간단**: 기존 CoT 프롬프트에 temperature 조정과 투표 로직만 추가하면 된다

**한계:**
- **계산 비용 증가**: 여러 번의 추론이 필요하므로 비용이 증가한다
- **시간 지연**: 실시간 응답이 필요한 경우 부적합할 수 있다
- **일관성 보장 불가**: 모든 샘플이 같은 오답을 낼 가능성도 있다

## 3. Tree of Thoughts 기법: 복잡한 문제 해결을 위한 탐색

**Tree of Thoughts (ToT)**는 Chain-of-Thought를 확장하여, 모델이 **여러 갈래의 사고를 나무(tree) 구조로 탐색**하도록 한 프레임워크다. Yao 등(2023)이 제안한 ToT의 핵심 개념은, 모델에게 문제 해결 중간단계(생각)를 하나씩 생성하게 하되 **여러 대안 분기**를 만들어 탐색하고, 각 단계마다 **자체 평가**를 통해 유망한 가지를 선택하거나 불필요한 가지는 가지치기(backtracking)하는 것이다. 이로써 LLM은 **미리 내다보는 전략적 사고**(lookahead)를 흉내내며, 복잡한 문제에서도 보다 체계적으로 탐색할 수 있게 된다.

ToT 알고리즘은 일반적으로 BFS/DFS 등의 **검색 기법**과 결합된다. 예를 들어, 어떤 문제를 풀 때 3단계의 중간 사고가 필요하다면, 1단계에서 여러 후보 생각을 만들고, **각각에 대해 2단계 후보**들을 전개한 뒤, 최종적으로 3단계까지 진행하면서 **"해결 가능성"을 모델이 평가**하여 가지를 선택한다. 모델은 각 중간 생각에 대해 *"이 경로가 해결로 이어질 것 같다(가능)"* / *"불가능할 것 같다"* 등을 표시하여, **가능성 높은 경로만 남기는** 방식으로 탐색 효율을 높인다.

### 3.1 Game of 24 성능 향상 사례

ToT의 위력은 수학 퍼즐 *24 게임*에서 극명하게 드러났다. *24 게임*은 주어진 4개의 숫자를 모두 사용하여 24를 만드는 수식을 찾는 문제인데, GPT-4를 **기존 CoT 프롬프트**로만 풀게 하면 **성공률 4%**에 불과했다. 반면 동일한 GPT-4에게 **Tree of Thoughts 전략**을 적용하자, **성공률이 무려 74%**까지 상승했다. 이는 ToT가 여러 경로의 탐색을 통해 정답에 도달하는 비율을 극적으로 높였음을 보여준다. 연구 결과에 따르면, ToT는 창의적 글쓰기, 미니 크로스워드 등 **탐색과 계획이 필요한 과제 전반**에서 기존 CoT보다 월등한 성능을 보였다.

### 3.2 Tree of Thoughts 구현 예제

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
        """현재 상황에서 가능한 다음 생각들을 생성"""
        
        if current_thoughts is None:
            current_thoughts = []
        
        context = f"문제: {problem}\n"
        if current_thoughts:
            context += f"현재까지의 생각: {' -> '.join(current_thoughts)}\n"
        
        prompt = f"""{context}

위 문제를 해결하기 위한 다음 단계의 가능한 접근 방법들을 3-5개 제시해주세요.
각 접근 방법은 구체적이고 실행 가능해야 합니다.

형식:
1. [접근 방법 1]
2. [접근 방법 2]
3. [접근 방법 3]
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
            print(f"생각 생성 중 오류: {e}")
            return []
    
    def evaluate_thought(self, problem: str, thought_path: List[str]) -> float:
        """생각 경로의 유망성을 평가 (0-1 점수)"""
        
        context = f"문제: {problem}\n"
        context += f"생각 경로: {' -> '.join(thought_path)}\n"
        
        prompt = f"""{context}

위 생각 경로가 문제 해결에 얼마나 유망한지 0-10점으로 평가해주세요.
평가 기준:
- 논리적 일관성
- 문제 해결 가능성
- 실행 가능성

점수만 숫자로 답해주세요 (예: 7)"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text) / 10.0  # 0-1 범위로 정규화
            return score
            
        except Exception as e:
            print(f"평가 중 오류: {e}")
            return 0.0
    
    def solve_with_tot(self, problem: str, max_depth: int = 3, beam_width: int = 3) -> Dict[str, Any]:
        """Tree of Thoughts로 문제 해결"""
        
        # 초기 상태
        current_paths = [[]]  # 빈 경로로 시작
        best_solution = None
        best_score = 0.0
        
        for depth in range(max_depth):
            print(f"\n=== 깊이 {depth + 1} ===")
            new_paths = []
            
            for path in current_paths:
                # 현재 경로에서 다음 생각들 생성
                next_thoughts = self.generate_thoughts(problem, path)
                print(f"경로 {path}: {len(next_thoughts)}개 후보 생성")
                
                for thought in next_thoughts:
                    new_path = path + [thought]
                    score = self.evaluate_thought(problem, new_path)
                    
                    print(f"  '{thought}' -> 점수: {score:.2f}")
                    
                    new_paths.append((new_path, score))
                    
                    # 최고 점수 업데이트
                    if score > best_score:
                        best_score = score
                        best_solution = new_path
            
            # 상위 beam_width개 경로만 유지
            new_paths.sort(key=lambda x: x[1], reverse=True)
            current_paths = [path for path, score in new_paths[:beam_width]]
            
            print(f"상위 {beam_width}개 경로 유지")
        
        return {
            "best_solution": best_solution,
            "best_score": best_score,
            "all_paths": current_paths
        }
    
    def _parse_thoughts(self, text: str) -> List[str]:
        """생성된 텍스트에서 생각들을 파싱"""
        thoughts = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # 번호나 불릿 포인트 제거
                thought = line.split('.', 1)[-1].strip()
                if thought.startswith('- '):
                    thought = thought[2:].strip()
                if thought:
                    thoughts.append(thought)
        
        return thoughts

# 사용 예시
def solve_24_game(numbers: List[int]):
    """24 게임 해결"""
    problem = f"주어진 숫자 {numbers}를 사용하여 24를 만드는 수식을 찾으세요. 각 숫자는 정확히 한 번씩만 사용해야 합니다."
    
    tot = TreeOfThoughts()
    result = tot.solve_with_tot(problem, max_depth=3, beam_width=3)
    
    print(f"\n=== 최종 결과 ===")
    print(f"최고 점수: {result['best_score']:.2f}")
    print(f"최적 경로: {' -> '.join(result['best_solution'])}")
    
    return result

# 예시 실행
numbers = [4, 6, 8, 2]
result = solve_24_game(numbers)
```

**출력 예시:**
```
=== 깊이 1 ===
경로 []: 4개 후보 생성
  '먼저 두 숫자를 곱해서 큰 수를 만들어보자' -> 점수: 0.60
  '더하기와 빼기를 조합해보자' -> 점수: 0.50
  '나누기를 활용해보자' -> 점수: 0.70
  '괄호를 사용한 복합 연산을 시도해보자' -> 점수: 0.80

상위 3개 경로 유지

=== 최종 결과 ===
최고 점수: 0.90
최적 경로: 괄호를 사용한 복합 연산을 시도해보자 -> (8-4) * (6-2) = 4 * 4 = 16 -> 16 + 8 = 24
```

### 3.3 Tree of Thoughts의 장점과 한계

**장점:**
- **체계적 탐색**: 여러 가능성을 체계적으로 탐색하여 최적해에 도달할 가능성이 높다
- **백트래킹**: 잘못된 경로를 조기에 포기하여 효율성을 높인다
- **복잡한 문제 해결**: 단순한 CoT로는 해결하기 어려운 복잡한 문제에 효과적이다

**한계:**
- **계산 비용**: 여러 경로를 탐색하므로 비용이 크게 증가한다
- **평가 주관성**: 모델이 스스로 평가하므로 일관성이 떨어질 수 있다
- **구현 복잡성**: 단순한 CoT보다 구현이 복잡하다

## 4. DSPy 프레임워크: 선언형 프롬프트 프로그래밍

프롬프트 엔지니어링을 **보다 체계적이고 모듈화**하기 위한 혁신적 접근으로 **DSPy** 프레임워크가 등장했다. DSPy(Declarative **Self-Improving** Python)는 프롬프트를 일종의 **프로그램**으로 취급하여, **선언형(declarative)**으로 작성하고 자동 최적화까지 지원하는 프레임워크다. 이를 통해 일일이 프롬프트 문장을 수정하는 대신, 구조화된 코드로 AI 동작을 기술하고 관리할 수 있다.

### 4.1 DSPy의 핵심 구성 요소

DSPy의 **구조**는 세 가지 핵심 요소로 이루어진다:

#### Signature(시그니처)
해결하려는 작업의 **입력과 출력 형식**을 선언한다. 마치 함수의 시그니처를 정의하듯이, 어떤 입력 필드를 받고 어떤 출력 필드를 생성할지 명시한다. 예를 들어 "question -> answer: float"와 같이 문자열로 간단히 표현하거나, Python 클래스 상속을 통해 상세히 정의할 수 있다. 시그니처는 **필드 타입**까지 지정할 수 있어, DSPy는 이를 기반으로 프롬프트 틀을 자동 생성하고 응답을 해당 타입으로 파싱한다.

#### Module(모듈)
프롬프트를 생성하고 모델을 호출하는 **전략**을 캡슐화한다. Signature를 토대로 어떤 프롬프팅 기법을 쓸지 선택하는 역할을 한다. DSPy는 다양한 모듈을 제공한다:

- **dspy.Predict**: 기본적인 단일 질문-응답 프레임을 생성한다
- **dspy.ChainOfThought**: Chain-of-Thought 방식으로 **중간 추론과 최종 답**을 모두 포함하는 프롬프트를 만든다
- **dspy.ReAct**: Tool 사용과 반응형 추론(ReAct)을 적용한 에이전트 프롬프트를 구성한다
- **BestOfN, Parallel, Refine** 등 복잡한 파이프라인용 모듈들

사용자는 시그니처에 맞춰 모듈을 선택하면, DSPy가 해당 전략에 맞게 **프롬프트를 조립**해 준다. 예컨대, 수학 문제에 ChainOfThought 모듈을 적용하면, "**[[문제]]**\n{question}\n**[[풀이]]**\n...**[[답]]**..." 같은 구조화된 프롬프트가 자동 생성된다.

#### Optimizer(최적화기)
DSPy의 비밀 병기로서, 프롬프트(또는 모델 파라미터)를 **자동으로 튜닝**해주는 알고리즘이다. Optimizer는 (i) DSPy 프로그램(모듈들의 조합), (ii) 평가 지표(metric 함수), (iii) 소량의 훈련 입력을 받아 동작한다. Optimizer는 LLM을 활용해 더 나은 지침문이나 예시를 생성하고, 여러 후보 프롬프트를 **탐색 및 평가**하여 성능을 최대화하는 방향으로 프롬프트를 개선한다. 

예를 들어 **MIPROv2**라는 최적화기는, 초기에 프로그램을 여러 입력에 실행해본 **추론 기록(trace)**을 수집하고 높은 점수의 경로를 선별한 뒤, 이를 바탕으로 지침문을 변형/제안하고 최종적으로 **조합 탐색**을 통해 최적의 프롬프트를 찾아낸다. 이러한 과정을 통해 Optimizer는 사람이 직접 튜닝하지 않아도 **Few-shot 예제 구성, 지시문 재구성, 파인튜닝**까지 자동화할 수 있다. DSPy에는 MIPROv2 외에도 **Bootstrap** 시리즈, **Ensemble**, **SIMBA** 등 다양한 자동 프롬프트 최적화 알고리즘이 내장되어 있다.

### 4.2 DSPy 실습 예제

```python
import dspy
from typing import Literal

# 1. 시그니처 정의
class SentimentCls(dspy.Signature):
    """Classify sentiment of a given sentence."""
    sentence: str = dspy.InputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()
    confidence: float = dspy.OutputField()

# 2. 모듈 생성
classifier = dspy.Predict(SentimentCls)

# 3. 사용 예시
result = classifier(sentence="This book was super fun to read, though not the last chapter.")
print(f"감정: {result.sentiment}, 신뢰도: {result.confidence}")
```

**출력 예시:**
```
감정: positive, 신뢰도: 0.85
```

위 코드에서 SentimentCls 시그니처를 정의하고, dspy.Predict 모듈을 사용해 프롬프트를 생성한다. DSPy는 자동으로 **시스템 메시지**에 입력/출력 필드를 설명하고, 사용자 메시지에 실제 입력값을 넣어 프롬프트를 구성한다. 모델의 응답은 DSPy에 의해 result.sentiment, result.confidence와 같이 **구조화된 출력**으로 파싱된다. 이를 통해 프롬프트 작성이 코드 수준에서 **재현 가능**하고 **모듈화**되며, 이후 **Optimizer를 통해 성능 개선**까지 손쉽게 연결할 수 있다.

### 4.3 DSPy의 장점과 한계

**장점:**
- **모듈화**: 프롬프트를 재사용 가능한 컴포넌트로 구성할 수 있다
- **자동 최적화**: Optimizer를 통해 프롬프트를 자동으로 개선할 수 있다
- **타입 안전성**: 입력/출력 타입을 명시하여 오류를 줄인다
- **재현성**: 코드로 프롬프트를 관리하여 재현 가능하다

**한계:**
- **학습 곡선**: 새로운 개념과 패러다임을 익혀야 한다
- **제한적 모듈**: 모든 프롬프팅 기법이 모듈로 제공되지 않는다
- **성능 의존성**: 최적화 결과가 평가 지표에 크게 의존한다

## 5. 자동 프롬프트 최적화(APE)와 최신 동향

프롬프트를 사람 손으로 실험하며 최적화하는 과정은 매우 번거롭기 때문에, **자동 프롬프트 최적화**에 대한 연구가 활발하다. 이를 가리켜 흔히 **Automated Prompt Engineering (APE)**이라 부르며, LLM 자체를 활용해 최적의 지시문이나 예제를 **검색**하거나 **진화**시키는 접근이다.

### 5.1 Automatic Prompt Engineer (APE)

**Automatic Prompt Engineer (APE)** 기법은 **프롬프트를 프로그램으로 간주한 최적화 문제**로 정의한다. Zhou 등(2022)의 APE 논문에서는, **LLM이 후보 지시문들을 생성**하고, 별도의 검증 모델로 각 후보의 성능을 평가하여 **최고 성능의 프롬프트**를 선택하는 루프를 제안했다. 이 방법을 통해 여러 NLP 과제에서 사람 작성 프롬프트보다 뛰어난 성능을 보였고, 24개 과제 중 19개에서 인간이 디자인한 프롬프트 수준 혹은 그 이상의 결과를 얻었다.

### 5.2 OPRO (Optimization by PROmpting)

최신 연구 중 하나인 **OPRO (Optimization by PROmpting)**는 아예 **LLM을 최적화 도구**로 활용하는 방법이다. 사람이 명시적으로 프롬프트를 만들지 않고, "**목표 성능을 높이는 프롬프트**"를 찾는 **자연어 최적화 문제**로 변환하여 LLM이 단계적으로 더 나은 프롬프트를 생성하도록 한다. 예를 들어 OPRO는 먼저 현재까지 생성된 프롬프트들과 성능을 요약하여 LLM에 제시하고, **다음 iteration의 새로운 프롬프트**를 출력받는 식으로 반복한다. 이렇게 하면 점진적으로 점수가 개선되는 방향으로 프롬프트가 진화한다.

### 5.3 성능 향상 사례

이러한 자동 기법들은 실제로 **최첨단 성능**을 달성하는 데 크게 기여하고 있다. 특히 **수학 문제** 벤치마크인 GSM8K에서, APE 기반 방법들이 GPT-4 수준의 성능까지 도달하는 사례가 나왔다. 한 예로, 오픈소스 **Ape** 도구는 GSM8K **정답률 93%**를 달성하여, 동일 모델의 기본 프롬프트 성능(70%)이나 DSPy 최적화 성능(86%)보다 훨씬 높았다. Google 연구진의 OPRO 기법 역시 **인간 설계 프롬프트 대비 GSM8K 정확도를 8%p 이상 향상**시켜 SOTA에 근접한 결과를 보고하였고, Big-Bench Hard와 같은 난해한 과제에서도 최대 50%p 향상을 이루었다고 한다.

또 다른 흥미로운 방향으로, **PromptWizard**와 같은 프레임워크에서는 LLM의 **피드백 주도(feedback-driven) 반복**으로 프롬프트와 few-shot 예제를 함께 최적화하는 전략을 취하고 있으며, **PanelGPT**처럼 여러 LLM이 토론하듯 프롬프트를 평가/개선하는 아이디어도 제시되고 있다. 이러한 도구와 논문들은 모두 **프롬프트 자동 개선**을 통해 모델의 잠재력을 극대화하려는 흐름에 있다.

### 5.4 자동 프롬프트 최적화의 의의

요약하면, 자동 프롬프트 최적화(APE)는 최신 LLM 시대에 등장한 **"프롬프트를 위한 AutoML"**이라고 할 수 있다. 이를 통해 최소한의 인적 개입으로도 높은 성능의 지시문을 얻을 수 있으며, 실제 오픈소스로도 **PromptChef/Ape**, **DSPy Optimizer**, **PromptWizard** 등이 공개되어 연구자와 개발자를 돕고 있다.

## 6. 실습 예시: DSPy를 활용한 프롬프트 자동 최적화 파이프라인

마지막으로, 앞서 소개한 DSPy 프레임워크를 이용하여 **프롬프트 자동 최적화** 파이프라인을 구성하는 실습 예시를 살펴보자. 여기서는 간단한 분류 문제를 예로 들어, **문제 정의 → Signature/Module 구성 → Optimizer로 개선 → 성능 확인**의 단계를 거친다.

### 6.1 문제 정의

예를 들어 *역사적 사건 설명*을 입력으로 받아 **사건의 분야**를 분류하는 과제를 생각해보자. 출력 레이블은 "전쟁/분쟁", "정치/통치", "과학/기술" 등 10여 개 카테고리 중 하나다. 모델의 출력에 **confidence score**도 포함시켜 불확실성도 확인하도록 설정한다.

### 6.2 Signature & Module 구성

우선 DSPy에서 시그니처 클래스를 정의한다.

```python
from typing import Literal
import dspy

# 1. 시그니처 정의
class CategorizeEvent(dspy.Signature):
    """Classify historic events into categories."""
    event: str = dspy.InputField()
    category: Literal["Wars", "Politics", "Science", "Culture", "Economics"] = dspy.OutputField()
    confidence: float = dspy.OutputField()

# 2. 모듈 생성
classifier = dspy.Predict(CategorizeEvent)

# 3. 초기 성능 평가 (예시)
test_events = [
    "제2차 세계대전이 1939년에 시작되었다",
    "아인슈타인이 상대성이론을 발표했다",
    "프랑스 혁명이 1789년에 일어났다"
]

# 4. Optimizer를 통한 자동 개선
from dspy.teleprompt import MIPROv2

def validate_category(example, prediction):
    return 1.0 if example.category == prediction.category else 0.0

optimizer = MIPROv2(metric=validate_category, auto="light")
optimized_classifier = optimizer.compile(classifier, trainset=train_examples)

# 5. 성능 개선 확인
result = optimized_classifier(event="아인슈타인이 상대성이론을 발표했다")
print(f"분류: {result.category}, 신뢰도: {result.confidence}")
```

위와 같이 Signature에 입력(event)과 출력(category, confidence) 필드를 선언하면, DSPy가 해당 구조를 따라 **기본 프롬프트**를 만들어낸다. dspy.Predict 모듈은 0-shot 프롬프트를 생성하므로, 이 상태에서 모델을 호출하면 아직 최적화되지 않은 **보일러플레이트 프롬프트**로 분류 작업을 수행하게 된다.

### 6.3 DSPy 최적화 과정

1. **초기 성능 평가**: 준비된 classifier 모듈을 가지고 소량의 예시 입력에 대한 성능(분류 정확도)을 측정한다. 예컨대 위 과제에 대해 20개의 역사 사건 설명을 정답 레이블과 함께 평가했더니 **정확도 52%** 정도가 나왔다고 가정한다.

2. **Optimizer 적용**: DSPy의 **MIPROv2**를 사용하여 프롬프트를 최적화한다. MIPROv2는 모델 가중치는 건드리지 않고 **프롬프트 자체**를 개선하는 데 초점을 맞춘 알고리즘이다. compile을 호출하면 MIPROv2가 내부적으로 다음을 수행한다:
   - classifier 모듈을 다양한 입력에 실행해보고, 모델 응답을 수집하여 현재 프롬프트의 성능을 측정
   - LLM을 사용해 프롬프트 지시에 대한 여러 **변형 후보**를 생성하거나, 필요한 경우 few-shot 예시 추가 등을 시도
   - 다양한 후보 프롬프트로 미니 배치 평가를 반복하며 점수가 올라가는 방향으로 **탐색**

3. **성능 개선 확인**: 최적화된 모듈을 동일한 평가 세트에 적용하여 성능을 다시 측정한다. 가령, **정확도가 63%로 향상**되었다면 초기 대비 상당한 개선이다. 실제 사례에서도, DSPy의 optimizer가 **약 51.9%에서 63.0%로** 정확도를 끌어올린 보고가 있다.

이러한 과정을 통해, DSPy를 사용한 **선언형 프롬프트 설계**와 **자동 최적화** 파이프라인을 구축할 수 있다. 이런 접근은 사람이 직접 프롬프트를 개선하는 데 비해 훨씬 **효율적**이며, 모델의 잠재력을 **체계적으로 끌어올릴** 수 있는 강력한 도구다.

---

## 체크포인트 질문

1. **역할 프롬프트(Role Prompting)** 기법은 무엇이며, 모델의 응답에 어떠한 영향을 주는가? 또 적용 시 유의해야 할 점은 무엇인가?

2. **Self-Consistency 디코딩**은 어떻게 동작하며, 왜 Chain-of-Thought 프롬프팅의 성능을 향상시킬 수 있을까? GSM8K에서의 성능 개선 수치를 설명해보라.

3. **Tree of Thoughts(ToT)** 기법은 어떤 방식으로 문제 해결을 수행하는가? ToT가 *Game of 24* 퍼즐에서 보여준 성능 향상은 어느 정도였는지 언급하라.

4. **DSPy의 Signature, Module, Optimizer**는 각각 무엇을 의미하며, 어떤 역할을 하는가? 이를 활용하면 프롬프트 엔지니어링에 어떤 이점이 있는가?

5. **자동 프롬프트 최적화(APE)**란 무엇인가? 사람이 작성한 프롬프트와 비교했을 때 APE 기법이 달성한 notable한 성과를 GSM8K 예시를 들어 설명하라.

6. 주어진 문제에 대해 **DSPy와 Optimizer**를 사용하여 프롬프트를 개선하는 절차를 간략히 요약해보라 (Signature 정의 → 모듈 실행 → Optimizer 적용 → 결과 확인). 또한 이러한 자동 최적화의 장점을 설명해보라.

---

## 참고자료

### 주요 논문 및 연구 자료

- Wang, X., et al. (2022). "Self-Consistency Improves Chain of Thought Reasoning in Language Models." arXiv preprint arXiv:2203.11171.
- Yao, S., et al. (2023). "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." arXiv preprint arXiv:2305.10601.
- Zhou, D., et al. (2022). "Large Language Models Are Human-Level Prompt Engineers." arXiv preprint arXiv:2211.01910.
- Yang, C., et al. (2023). "Large Language Models as Optimizers." arXiv preprint arXiv:2309.03409.

### 기술 문서 및 구현체

- DSPy Official Documentation: https://dspy.ai/
- Learn Prompting: https://learnprompting.org/
- Prompt Engineering Guide: https://www.promptingguide.ai/
- PromptWizard Framework: https://microsoft.github.io/PromptWizard/

### 온라인 리소스 및 블로그

- "Role Prompting: Guide LLMs with Persona-Based Tasks" - Learn Prompting
- "Prompt Architectures: An Overview of structured prompting strategies" - Medium
- "Tree of Thoughts (ToT)" - Prompt Engineering Guide
- "Pipelines & Prompt Optimization with DSPy" - Technical Blog
- "Best Free Prompt Engineering Tools of 2025" - SourceForge

### 벤치마크 및 평가 자료

- GSM8K: Grade School Math 8K Dataset
- Game of 24: Mathematical Puzzle Benchmark
- Big-Bench Hard: Challenging Language Understanding Tasks
