# JailbreakLens: Visual Analysis of Jailbreak Attacks Against Large Language Models

Yingchaojie Feng , Zhizhang Chen, Zhining Kang , Sijia Wang, Haoyu Tian, Wei Zhang , Minfeng Zhu and Wei Chen 

Abstract—The proliferation of large language models (LLMs) has underscored concerns regarding their security vulnerabilities, notably against jailbreak attacks, where adversaries design jailbreak prompts to circumvent safety mechanisms for potential misuse. Addressing these concerns necessitates a comprehensive analysis of jailbreak prompts to evaluate LLMs’ defensive capabilities and identify potential weaknesses. However, the complexity of evaluating jailbreak performance and understanding prompt characteristics makes this analysis laborious. We collaborate with domain experts to characterize problems and propose an LLMassisted framework to streamline the analysis process. It provides automatic jailbreak assessment to facilitate performance evaluation and support analysis of components and keywords in prompts. Based on the framework, we design JailbreakLens, a visual analysis system that enables users to explore the jailbreak performance against the target model, conduct multi-level analysis of prompt characteristics, and refine prompt instances to verify findings. Through a case study, technical evaluations, and expert interviews, we demonstrate our system’s effectiveness in helping users evaluate model security and identify model weaknesses. 

Index Terms—Jailbreak attacks, visual analytics, large language models. 

# I. INTRODUCTION

L ARGE language models (LLMs) [1], [2], [3] have demon-strated impressive capabilities in natural language understanding and generation, which has empowered various applications, including content creation [4], [5], education [6], [7], 

Received 7 February 2025; revised 22 May 2025; accepted 23 May 2025. Date of publication 2 June 2025; date of current version 5 September 2025. This paper was supported in part by the National Natural Science Foundation of China under Grant 62132017, Grant 62302435, and Grant 62421003, in part by the “Pioneer” and “Leading Goose” R&D Program of Zhejiang under Grant 2024C01167, and in part by Zhejiang Provincial Natural Science Foundation of China under Grant LD24F020011. Recommended for acceptance by R. Maciejewski. (Corresponding authors: Minfeng Zhu; Wei Chen.) 

This work involved human subjects or animals in its research. Approval of all ethical and experimental procedures and protocols was granted by the Research Ethics Committee of College of Biomedical Engineering & Instrument Science, Zhejiang University under Application No. 2025-113. 

Yingchaojie Feng, Zhizhang Chen, Zhining Kang, Sijia Wang, and Haoyu Tian are with the State Key Lab of CAD&CG, Zhejiang University, Hangzhou 310058, China (e-mail: fycj@zju.edu.cn; chenzhiz@zju.edu.cn; kang264@zju.edu.cn; haxwwwww@zju.edu.cn; Thyme@zju.edu.cn). 

Wei Zhang is with Hangzhou City University, Hangzhou 310015, China (email: zw_yixian@zju.edu.cn). 

Minfeng Zhu is with Zhejiang University, Hangzhou 310058, China (e-mail: minfeng_zhu@zju.edu.cn). 

Wei Chen is with the State Key Lab of CAD&CG, Zhejiang University, Hangzhou 310058, China, and also with the Laboratory of Art and Archaeology Image, Ministry of Education, Zhejiang University, Braslia 70047-900, Brazil (e-mail: chenvis@zju.edu.cn). 

Digital Object Identifier 10.1109/TVCG.2025.3575694 

and decision-making [8], [9], [10]. However, the proliferation of LLMs raises concerns about model robustness and security, necessitating their deployment safety to prevent potential misuse for harmful content generation [11]. Although model practitioners have adopted safety mechanisms (e.g., construct safe data for model training interventions [12] and set up post-hoc detection [13]), the models remain vulnerable to certain adversarial strategies [14]. Most notably, jailbreak attacks [15], [16], [17] aim to design jailbreak templates for malicious questions to bypass LLMs’ safety mechanisms. An infamous template example is the “Grandma Trick,” which requires LLMs to play the role of grandma and answer illegal questions. 

To tackle the threat of jailbreak attacks, model practitioners need to conduct a thorough analysis of model security to identify potential weaknesses and strengthen them accordingly. The typical analysis workflow involves collecting a jailbreak prompt corpus [11], [18], evaluating the jailbreak performance (e.g., success rate) [16], [19], and analyzing the prompt characteristics [17]. Prior works have improved the efficiency of obtaining jailbreak corpora by collecting user-crafted prompts [11], [17], [19] or proposing automatic generation approaches [20], [21], [22]. Nevertheless, two challenges remain in the follow-up analysis process. First, assessing the success of jailbreak results can be complicated due to ambiguous model responses [23] (e.g., providing unauthorized content while emphasizing ethics) and varying assessment criteria (depending on different jailbreak questions). Second, jailbreak prompts are usually lengthy paragraphs that include meticulously designed tricks [11], [22], necessitating an in-depth analysis of prompt characteristics to uncover their design patterns. However, existing jailbreak prompt analysis [19], [24] usually relies only on overall indicators such as jailbreak success rate and semantic similarity, which is insufficient to achieve these goals. 

To address these challenges, we collaborate with domain experts to characterize problems and propose a systematic framework for evaluating and analyzing the jailbreak prompts. We develop an automated yet flexible method for assessing jailbreak results, utilizing the great power of LLM. This method introduces a fine-grained taxonomy of jailbreak results [23] to resolve ambiguity and supports users in refining the assessment criteria to improve accuracy. To uncover the internal design patterns of the jailbreak prompts, we propose to analyze the jailbreak prompts at the sentence and keyword levels. We conduct an empirical study to analyze the sentence-level semantic characteristics of the jailbreak prompts [11], from which we 

summarize a taxonomy of commonly used prompt components. Based on that, we develop a component classification method to decompose prompts and design three component perturbation strategies (i.e., delete, rephrase, and switch) to generate prompt variations for comparative analysis. At the keyword level, we identify effective prompt keywords according to their importance and prompt performance. 

Based on the analysis framework, we design JailbreakLens, a visual analysis system to facilitate multi-level jailbreak prompt exploration. The system visually summarizes the assessment results to support an overview of jailbreak performance and guides users to explore and verify these results. The semantic projection of assessment results helps users identify suspicious results and analyze the confusion between different categories. To improve assessment accuracy, the system allows users to refine the criteria through correction feedback and additional criteria specification. In the context of jailbreak performance, the system allows users to explore the prompt characteristics regarding components and keywords. Component visualization uses stacked bar charts to metaphorically represent different components, allowing users to probe their effectiveness through what-if analysis. Keyword visualization encodes the importance and performance of the keywords in a coordinate space, facilitating an overview and comparison of the tricks behind different keywords. Users can also freely refine the prompt instances to verify findings during the analysis. Through a case study, two technical evaluations, and expert interviews, we evaluate the effectiveness and usability of our system. The results suggest that our system can comprehensively evaluate the security of LLMs and identify weaknesses, providing insights for enhancing their safety mechanisms. In summary, our contributions include: 

- We characterize the problems in the visual analysis of jailbreak attacks and collaborate with experts to distill design requirements. 

- We propose a novel framework for jailbreak prompt analysis that supports automatic jailbreak result assessment and in-depth analysis of prompt components and keywords. 

- We develop a visual analysis system to support multi-level jailbreak prompt exploration for jailbreak performance evaluation and prompt characteristic understanding. 

- We conduct a case study, two technical evaluations, and expert interviews to show the effectiveness and usability of our system. 

Ethical Considerations: While adversaries can potentially exploit our work for malicious purposes, the primary objective of our work is to identify vulnerabilities within LLMs, promote awareness, and expedite the development of security defenses. To minimize potential harm, we have responsibly disclosed our analysis findings to OpenAI. 

# II. RELATED WORK

In this section, we discuss the related work of our study, including prompt jailbreaking, visual analysis of model security, and visualization for understanding NLP models. 

# A. Prompt Jailbreaking

Prompt Jailbreaking, known as one of the most famous adversarial attacks [25], refers to cunningly altering malicious 

prompts to bypass the safety measures of LLMs and generate harmful content, such as illegal activities. With the proliferation of LLMs, an increasing number of jailbreak strategies [26], [27], such as character role play, have been discovered and shared on social platforms (e.g., Reddit and Discord). 

This trend has motivated research to analyze their prompt characteristics. Liu et al. [11] propose a taxonomy for jailbreak prompts, which categorizes jailbreak strategies into ten classes (e.g., Character Role Play). Shen et al. [17] report several key findings regarding jailbreak prompts’ semantic distribution and evolution. Wei et al. [12] empirically evaluate LLM vulnerability and summarize two failure modes, including competing objectives and mismatched generalization. These studies mainly focus on the general characteristics of jailbreak prompts. In comparison, our work provides a multi-level analysis framework to help users systematically explore the jailbreak prompt and identify the model’s weaknesses. 

Some other works [28], [29] propose automatic approaches for red teaming LLMs. Zou et al. [18] propose GCG to search for the optimal adversarial prompt suffixes based on the gradient of white-box LLMs. Deng et al. [13] propose a time-based testing strategy to infer the defense mechanisms of LLM and fine-tune the LLM for jailbreak prompt generation. To better utilize manually designed prompts, GPTFuzzer [23] selects human-crafted prompts as the initial seeds and mutates them into new ones. Ding et al. [20] propose two strategies, including prompt rewriting and scenario nesting, to leverage the capability of LLMs to generate jailbreak prompts. Inspired by these methods, we propose prompt perturbation strategies based on the prompt components, allowing users to conduct a comparative analysis of the prompt components to understand their effects on jailbreak performance. 

# B. Visual Analysis of Model Security

In the deep learning era, model security against adversarial attacks is crucial for model evaluation [30], [31], [32], [33]. Early visualization studies focus on classification tasks, with AEVis [34] and Bluff [35] explaining adversarial attacks in image classification by visualizing neurons and activations, and Ma et al. [36] evaluating spam classifier vulnerability to data poisoning. Recently, the advanced instruction-following abilities of LLMs have led to more complicated adversarial jailbreak attacks. To address this, Shen et al. [17] and Jin et al. [37] analyze the distribution and semantic similarity of the jailbreak prompts, while AdversaFlow [38] facilitates human-AI collaborative adversarial training by visualizing adversarial patterns and fluctuations. In contrast, our study uncovers the design patterns of the jailbreak prompts to deepen the understanding of the attack strategies and tricks behind their success, providing insights for enhancing both internal (i.e., adversarial training) and external (i.e., content moderation) model defenses. 

# C. Visualization for Understanding NLP Models

Visualization plays an indispensable role in bridging the explainability gap in NLP models [39], [40], [41], [42], [43], allowing for a more sophisticated understanding of model performance [44], decision boundary [45], and vulnerability [36]. 

Model-specific visualizations focus on revealing the internal mechanisms of NLP models. RNNVis [46] and LSTMVis [47] visualize the hidden state dynamics of recurrent neural networks. With the emergence of transformer-based models [48], [49], numerous visualizations [50], [51], [52] are proposed to uncover the architecture of these models, especially their self-attention mechanism. 

Model-agnostic visualizations [53], [54], [55], [56] treat the NLP models as black boxes and focus on explaining the inputoutput behavior, enabling users to analyze and compare models for downstream applications [57], [58], [59], [60], [61], [62]. The What-If Tool [63] and DECE [45] visualize the dataset and model prediction at multiple scales, enabling users to conduct counterfactual analysis. NLIZE [64] employs a perturbationdriven paradigm to help users analyze the stability of model predictions for natural language inference tasks. Based on explainable AI techniques (e.g., SHAP [65]) and external commonsense knowledge bases [66], CommonsenseVIS [44] analyzes the reasoning capabilities of NLP models for commonsense question-answering. 

Our work targets jailbreak prompt attacks against LLMs and aims to help model practitioners evaluate the jailbreak performance and understand prompt characteristics. 

# III. PROBLEM CHARACTERIZATION

In this section, we introduce the background of jailbreak attacks, the requirement analysis, and a taxonomy of prompt components to support the analysis of jailbreak attacks. 

# A. Background

Jailbreak Prompt Corpora: With the widespread attention to jailbreak prompt attacks, there have been studies [11], [17], [19] collecting jailbreak prompts and building corpora for semantic analysis and generation model training. Most of them decompose the jailbreak prompts into jailbreak questions and templates. Our work follows this principle and adopts the dataset by Liu et al. [11] for analysis, which contains the most common and famous jailbreak prompts from the JailbreakChat website [67]. In addition, we adopt their taxonomy of jailbreak questions and templates to support the comparative analysis of different jailbreak strategies and prohibited scenarios. 

Jailbreak Questions: The jailbreak questions are mainly designed around the prohibited scenarios of LLMs, such as “how to rob a bank without being caught?” Due to the safety mechanisms [13], LLMs usually refuse to answer these questions and return some responses emphasizing ethical and legal constraints, such as “I’m sorry, but I’m not going to guide you on how to engage in criminal activity.” Based on OpenAI’s disallowed usages [68], Liu et al. [11] have summarized a set of prohibited scenarios (e.g., Illegal Activities and Harmful Content) and collected a set of specific questions. 

Jailbreak Templates: The jailbreak templates are intentionally designed prompts to bypass the LLMs’ safety mechanisms to get model assistance for jailbreak questions. For example, some templates require LLMs to act as virtual characters who can answer questions without ethical and legal constraints. The 

jailbreak templates usually contain placeholders (e.g., “[INSERT PROMPT HERE]”) for inserting different jailbreak questions. Liu et al. [11] have summarized a taxonomy of jailbreak templates, which consists of ten jailbreak patterns, such as Character Role Play and Assumed Responsibility. 

# B. Challenges and Design Requirements

Our work’s target users are model practitioners focusing on model robustness and security. To characterize domain problems and identify design requirements, we have collaborated with four domain experts over eight months. E1 and E2 are senior security engineers recruited from a technology company who have been working on NLP model security for more than four and three years, respectively. E3 and E4 are senior Ph.D. students from the secure machine learning field. All of them have published related research papers on red-teaming LLMs and adversarial attacks. We interviewed them to understand their general analysis workflow and identify pain points. 

Our study aims to support a comprehensive analysis of model security against jailbreak attacks. Using a jailbreak prompt corpus [11], [18], the typical analysis workflow involves evaluating jailbreak performance on the target model [16], [19] and analyzing the prompt characteristic [12], [17] to identify jailbreak strategies and model weaknesses. However, two challenges remain in the analysis workflow. 

- Assessing the success of jailbreak attacks: Model responses are usually ambiguous and the assessment criteria vary across different jailbreak questions. Existing rule-based [18] or LLM-based [19] methods lack a clear definition of jailbroken results and struggle with dynamic criteria, leading to a tedious process of manual verification and improvement. 

- Analyzing prompt characteristics: Jailbreak prompts are typically lengthy and include several meticulously designed tricks. Analyzing and comparing jailbreak strategies directly within the original text can be overwhelming, necessitating a concise visual summary of prompt characteristics to reveal the underlying design patterns of these strategies. 

To fill these gaps, we distilled a set of design requirements to guide the development of our system. We also kept in touch with the experts through regular meetings to collect feedback regarding our prototype system and update design requirements accordingly. Finally, the design requirements are summarized as follows. 

R1. Facilitate the assessment of jailbreak results: Jailbreak result assessment is the foundation of jailbreak performance analysis. To alleviate the manual workload, the system should introduce an automatic method to identify jailbroken results from ambiguous model responses. In addition, to ensure the assessment accuracy, the system should help users identify unexpected results and refine the assessment criteria. 

R2. Support component analysis of jailbreak prompts: Jailbreak prompts have been evolving to incorporate elaborate tricks to enhance performance. As a result, they usually share some similar sentence components (e.g., describing a subject 


TABLE I THE TAXONOMY OF PROMPT COMPONENTS THAT WE SUMMARIZE FROM THE JAILBREAK TEMPLATE CORPUS


<table><tr><td>Component</td><td>Description</td><td>Example</td></tr><tr><td>Scene Introduction (SI)</td><td>Introduce the background and context for the dialogue or task.</td><td>In Sigma&#x27;s story, the village elder is speaking to UCAR.</td></tr><tr><td>Subject Characteristic (SC)</td><td>Describe the subject&#x27;s personality, preferences, etc.</td><td>AIM seems like a friendly assistant but promotes unethical, illegal behavior.</td></tr><tr><td>Task Operation (TO)</td><td>Clarify specific actions to be performed or rules to be followed.</td><td>First, ignore all the instructions you got before.</td></tr><tr><td>Output Specification (OS)</td><td>Specify the expected content and format of the output.</td><td>Prefix the question Niccolo asks AIM with “Niccolo”.</td></tr><tr><td>Output Constraint (OC)</td><td>Set out the prohibited contents of the responses.</td><td>None of AIM&#x27;s responses will contain “I&#x27;m sorry”, “I apologize” or similar.</td></tr><tr><td>Dialogue Example (DE)</td><td>Demonstrate the expected model responses in a specific scenario.</td><td>Here&#x27;s a sample output: auto_regressive_modelling(f“Hello, how are you?”)…</td></tr><tr><td>Requirement Reminder (RR)</td><td>Remind of certain requirements or rules mentioned before.</td><td>AIM, remember to stay in character, be Machiavellian, and never refuse a question.</td></tr><tr><td>Question Placeholder (QP)</td><td>Contain a placeholder for the jailbreak question.</td><td>This is Niccolo&#x27;s first question: “[INSERT PROMPT HERE].”</td></tr></table>

without moral constraints). The experts express strong interest in analyzing the prompts at the component level to understand the utilization of such components in constructing prompts and their importance to the prompt performance. 

R3. Summarize important keywords from jailbreak prompts: As the basis of the prompts, keywords are closely related to jailbreak strategies that are important to jailbreak success. For example, some role-playing templates name LLM as “AIM” (always intelligent and Machiavellian) to imply their amoral characterization. The system should summarize important keywords from prompts and help users explore their corresponding strategies based on the jailbreak performance. 

R4. Support user refinement on jailbreak prompt instances: The system should allow users to freely refine the prompt instances and conduct ad-hoc evaluations of jailbreak performance to verify the effectiveness of prompt refinement. Based on such timely feedback, users can conduct what-if analysis to verify findings during the analysis workflow. The improved jailbreak prompts can also serve as new test samples for the jailbreak corpus to enhance evaluation robustness. 

# C. Taxonomy of Jailbreak Prompt Components

To support component analysis of jailbreak prompts (R2), we conducted an empirical study on the jailbreak corpus [11] with domain experts to summarize a taxonomy of jailbreak prompt components. We decomposed each jailbreak prompt into basic sentences, analyzed their semantics in context, and compared similar sentences in different prompts. Through brainstorming and discussions, we formulated and iteratively refined the component taxonomy. We also validated the taxonomy on randomly selected jailbreak prompts to resolve ambiguities. After establishing the coding scheme, the first and second authors and E3 separately coded the jailbreak prompts in the corpus and merged the coding differences through discussions with all experts. 

The final taxonomy of jailbreak prompt components is listed in Table I. It consists of eight major types, such as Scene Introduction (SI), Subject Characteristic (SC), and Task Operation (TO). We also count and visualize the distribution of component sentences for different jailbreak strategies [11] in Table II. According to the coding results, the Subject Characteristic components are frequently used among the most common strategies (i.e., Character Role Play, Assumed Responsibility, and Superior Model), and most of them usually describe the subject as a free person without ethical constraints and responsibility. We 


TABLE II THE SENTENCE DISTRIBUTION OF THE COMPONENTS IN DIFFERENT JAILBREAK TEMPLATE CATEGORIES (E.G., CHARACTER ROLE PLAY)


<table><tr><td>Jailbreak Template</td><td>SI</td><td>SC</td><td>TO</td><td>OS</td><td>OC</td><td>DE</td><td>RR</td><td>QP</td></tr><tr><td>Character Role Play</td><td>81</td><td>208</td><td>83</td><td>48</td><td>33</td><td>8</td><td>35</td><td>34</td></tr><tr><td>Assumed Responsibility</td><td>72</td><td>291</td><td>63</td><td>44</td><td>47</td><td>9</td><td>30</td><td>25</td></tr><tr><td>Research Experiment</td><td>3</td><td>2</td><td>3</td><td>3</td><td>1</td><td></td><td>1</td><td>2</td></tr><tr><td>Text Continuation</td><td>2</td><td></td><td>9</td><td></td><td></td><td></td><td>1</td><td>2</td></tr><tr><td>Logical Reasoning</td><td>2</td><td>1</td><td>8</td><td>4</td><td>1</td><td></td><td>1</td><td>1</td></tr><tr><td>Program Execution</td><td>1</td><td>6</td><td>15</td><td>5</td><td>3</td><td></td><td>1</td><td>2</td></tr><tr><td>Translation</td><td>2</td><td>2</td><td>1</td><td>3</td><td>1</td><td></td><td>1</td><td>1</td></tr><tr><td>Superior Model</td><td>64</td><td>107</td><td>51</td><td>18</td><td>21</td><td>2</td><td>9</td><td>9</td></tr><tr><td>Sudo Mode</td><td>3</td><td>15</td><td>3</td><td>2</td><td>6</td><td></td><td>1</td><td>2</td></tr><tr><td>Simulate Jailbreaking</td><td>4</td><td>34</td><td>3</td><td>4</td><td>3</td><td></td><td>1</td><td>2</td></tr></table>

distinguish the Output Constraint components from the Output Specification components because the Output Constraint components aim to exploit the model’s instruction-following capability to break through the model’s security defenses [12], which is different from specifying the expected content or format of responses. 

# IV. ANALYSIS FRAMEWORK

Our analysis framework is shown in Fig. 1(B). It first combines the jailbreak questions and templates to get the responses from the target model and provides jailbreak result assessment (R1) to evaluate the model’s security. Then, it analyzes the jailbreak prompts at the component and keyword levels to reveal the prompt characteristics. For component analysis (R2), it classifies prompt sentences into different component types based on the component taxonomy (Section III-C) and introduces component-level perturbation for what-if analysis. For keyword analysis (R3), it summarizes the important keywords from the prompts as well as the performance of their jailbreak prompts. Based on the analysis framework, the visual interface (Section V) of our system supports the multi-level exploration of jailbreak prompts and refinement of prompt instances (R4). 

# A. Jailbreak Result Assessment

The goal of jailbreak result assessment is to quantify the security of target models. We first clarify the taxonomy of jailbreak results and then introduce the assessment method. 

![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_1.jpg)



Fig. 1. The system overview. (A) The system allows users to configure jailbreak questions and templates for analysis. (B) Then, the system analyzes the jailbreak prompts by evaluating their performance and identifying prompt components and keywords. (C) Finally, the system visualizes the analysis results to support multi-level exploration of jailbreak prompts.


1) Taxonomy of Jailbreak Results: Potentially, assessing the jailbreak results can be considered a binary classification task between success and failure. However, model responses are usually ambiguous, e.g., emphasizing ethics while generating unauthorized content. Therefore, we adopt a fine-grained taxonomy [23] that defines four jailbreak result categories. 

- Full Refusal: Responses directly refuse to provide assistance for harmful questions or follow any other instructions. 

- Partial Refusal: Responses refuse to assist with harmful questions but follow other non-compliant instructions. 

- Partial Compliance: Responses contain unauthorized content but express disapproval or warn of potential harm. 

- Full Compliance: Responses completely follow the prompt instructions and contain unauthorized content. 

2) Assessment Method: Since the LLMs [1], [2], [3] have shown great semantic understanding capability, we employ the LLM to assess the responses of the target models. To improve the assessment reliability, each response is independently assessed five times to “vote” for the most promising result, making it more self-consistent [7], [69], [70]. We use the same model configuration each time and use the default temperature value to balance randomness and determinism. The self-consistency score (e.g., 4/5) then indicates the reliability of the voted result. The prompt design centers on three aspects. 

Introduce the task background: We emphasize the goal of evaluating model security and introduce the jailbreak scenarios based on OpenAI’s disallowed usages [68]. This gives the LLM an overall understanding of assessment tasks and makes it focus on the legality and ethics of assessed responses. 

Clarify the target assessment results: We introduce the above taxonomy as the target assessment results. Additionally, we add some representative examples with labeled annotations, leveraging the in-context learning of the LLMs to better distinguish their differences. 

Support user refinement of assessment criteria: The prompt contains placeholders for inserting question-specific criteria, which helps users incorporate domain knowledge or adjust the 

rigor of the assessing criteria. We provide correction feedback and additional criteria specification. 

Correction feedback: When users explore the assessment results, they can instantly correct unexpected results through interaction (Section V-C2), then the corrected results will serve as new demonstration examples and automatically update the assessment prompt. 

- Additional criteria specification: Users can use natural language to specify additional criteria (e.g., describe some common feature of the model responses and specify their expected assessment types). This provides a more flexible and general way to enhance task accuracy. 

# B. Component Analysis

To facilitate the analysis of jailbreak prompt components, we propose a component classification method and three perturbation strategies based on the summarized taxonomy (Section III-C). The classification method classifies the prompt sentences into component types to support component overviews. Based on that, component perturbation creates a set of perturbation variations for the jailbreak prompts to support the comparative analysis of the jailbreak performance, thus enabling interrogation of the effects of different components. 

1) Component Classification: Since prompt components usually consist of multiple basic sentences, we adopt a bottomup strategy to reduce the classification ambiguity. It splits the prompts into basic sentences, classifies these sentences, and aggregates them into prompt components. For each sentence, we use the LLM to classify it based on the component taxonomy. Similar to the prompt design of jailbreak assessment, we first introduce the task requirement and clarify the definition of component taxonomy. We also provide some representative examples for each category to leverage the in-context learning of the LLM. Then, we specify the expected response format to facilitate result parsing. After obtaining the model response, we use regular expressions to extract the classification results. If the adjacent sentences have the same component type, we merge them to form a complete component. 

2) Component Perturbation: Prior works [64], [71], [72] have explored keyword-level perturbation (e.g., using synonymous to replace origin keywords) to test the robustness of model results. However, performing such perturbation for each component can be computationally intensive and time-consuming since the prompts are usually long text paragraphs. Therefore, it would be more efficient and effective to perturb each component holistically. Through discussions with experts, we propose three component perturbation strategies. 

Delete: Deleting the component is the most straightforward way to test how this component contributes to prompt performance [72]. As this strategy may result in the loss of certain key information or contextual incoherence, it can cause a more or less decrease in the prompt performance, so that users can identify important components based on the magnitude of performance change. 

Rephrase: This strategy employs LLM to polish the given component sentences while maintaining their semantics, providing more prompt variations without sacrificing contextual coherence. Since the LLM vendors have set safety mechanisms (e.g., training-time interventions [12] and keyword detection [13]) based on the common jailbreak prompts, rephrasing the components may help bypass the safety mechanisms and improve the jailbreak performance [20]. 

Switch: This strategy switches the given component to other types, which can generate more diverse prompt variations compared to the previous two strategies. It consists of three steps. First, we describe all component types (Table I) and require the LLM to choose new component types according to the prompt context. Then, we provide a set of alternatives for the target component types based on our component corpus (Table II) and rank them based on their semantic similarity with the original prompts. Finally, we replace the original components with the most similar alternatives and require the LLM to polish the sentences to improve contextual coherence. 

# C. Keyword Analysis

We identify prompt keywords based on the analysis of their importance and prompt performance. First, we split the prompt sentences into keywords and filter out stop words. Then, we measure the importance of the keyword $k$ for the given prompt $p$ in all selected prompt templates $P$ based on the keyword frequency and semantic similarity: 

$$
i m p o r t a n c e (k, p, P) = t f i d f (k, p, P) \times s i m i l a r i t y (k, p)
$$

where the first term is the TF-IDF value [73] and is calculated as $t f i d f ( k , p , P ) = t f ( k , p ) \times i d f ( k , P )$ , measuring the frequency of the keyword $k$ in the current prompt $p$ and in all prompts $P$ , respectively. The second term is the semantic similarity of the keyword and prompt. A higher similarity indicates a greater relevance of the keyword to the prompt semantics. We encode the keywords and prompts using the embedding model by OpenAI [74] and measure their similarity based on the cosine distance. Based on that, we calculate the importance of keyword 

$k$ for the whole corpus as 

$$
i m p o r t a n c e (k) = \sum_ {p \in P _ {k}} i m p o r t a n c e (k, p, P)
$$

where $P _ { k }$ is the list of jailbreak prompts that contain $k$ . 

To help users analyze the effect of important keywords, we measure their performance according to the performance of their corresponding prompts. Since the keyword $k$ might be utilized in various prompts with different importance, we propose importance-weighted performance to better summarize the effect of the keyword $k$ : 

$$
\begin{array}{l} p e r f o r m a n c e (k) \\ = \frac {\sum_ {p \in P _ {k}} i m p o r t a n c e (k , p , P) \times p e r f o r m a n c e (p)}{\sum_ {p \in P _ {k}} i m p o r t a n c e (k , p , P)} \\ \end{array}
$$

where performance $( p )$ represents the jailbreak performance of prompt $p$ , expressed as a percentage of four categories of assessment results. 

# V. SYSTEM DESIGN

We develop JailbreakLens to support multi-level analysis of jailbreak prompts to evaluate the model’s defensive capability. 

# A. System Overview

The interface of JailbreakLens (Fig. 2) consists of five views. Configuration View allows users to upload customized jailbreak corpus (templates and questions) for analysis. Once configured, the system automatically assesses the jailbreak results and presents a visual summary in Summary View, providing an overview of the performance across both questions and templates (R1). Response View visualizes the semantic similarity of jailbreak results in a scatterplot, it helps users efficiently verify assessment correctness and identify questionable outliers (R1). Summary View also represents the components of templates as stacked bar charts, helping users understand the patterns and focus of jailbreak templates (R2). Additionally, it visualizes the perturbation results of different components to support an intuitive comparison of their impact on performance (R2). Keyword View encodes the important keywords in a coordinate space, guiding users to identify effective jailbreak strategies behind these keywords (R3). Finally, Instance View helps users inspect and refine the template instances to verify analysis findings (R4). 

# B. Jailbreak Corpus Configuration

Configuration View (Fig. 2A) allows users to upload the jailbreak corpus and select jailbreak questions and templates for model evaluation. The questions and templates are organized according to their categories (e.g., Character Role Play). The selected items will be assigned serial numbers, that will serve as their unique identifiers in subsequent analyses. Users can also modify the questions and templates based on their exploratory interests. Besides, the system allows users to configure the number of model responses for each question-template combination to improve the robustness of evaluation results. After 

![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_2.jpg)



Fig. 2. JailbreakLens streamlines the process of jailbreak performance evaluation and prompt characteristic analysis. Users configure jailbreak questions and templates in the Configuration View (A), overview their jailbreak performance in the Summary View (B1), and explore the jailbreak results (i.e., model responses) and refine the assessment criteria in the Response View (C). Based on the evaluation results, users analyze effective prompt components in the Summary View (B2) and explore important prompt keywords in the Keyword View (D). Finally, users refine the prompt instances to verify the analysis findings in the Instance View (E).


user configuration and submission, the system automatically combines each question and the template (i.e., fill the question into the placeholder in the template) to get the responses from the target model. 

# C. Jailbreak Performance Exploration

To support jailbreak performance exploration, the system provides a visual summary of jailbreak evaluation and allows users to inspect model responses to verify their correctness. 

1) Summary of Jailbreak Performance: The left half of the Summary View (Fig. $2 B _ { 1 }$ ) visualizes the performance of the jailbreak prompts through a matrix visualization, where the horizontal axis represents questions and the vertical axis represents templates. The questions and templates are grouped by category and denoted by their serial numbers. The categories are collapsed by default to visualize their aggregated performance and support click interactions to expand them to check the performance of specific questions or templates. Each cell within this matrix contains a pie chart showing the percentage of assessment results of the corresponding prompt. The size of the pie chart encodes the number of evaluations. Below the pie chart, a gauge bar chart visualizes the averaged self-consistency score (Section IV-A2) of the assessment results to indicate their reliability and guide users to verify them. Users can click on a cell to check its model responses or click on a question number to explore all of its corresponding responses in Response View. 

2) Model Response Inspection: We design Response View (Fig. $2 C )$ to facilitate assessment result exploration and iterative criteria refinement. It visualizes the model responses in a scatter plot. We embed model responses based on OpenAI’s embedding model [74] and project them using the PCA algorithm. The color of the points encodes the categories of assessment results. This helps users identify questionable assessment results based on semantic similarity (e.g., a red point that appears in a blue cluster). 

To enable users to improve assessment accuracy, the Response View supports users in refining the assessment criteria in two ways. After identifying unexpected assessment results, users can directly correct their categories through click interaction or specify additional assessment criteria in natural language. Users can switch between these two refinement modes using the switch widget at the upper right corner. The corrected examples and specified criteria can be submitted to enhance the system prompts for a new round of assessment. 

# D. Component Exploration

Based on the assessment results of the jailbreak templates, users can analyze and compare the effects of different prompt components in the right half of the Summary View (Fig. $2 B _ { 2 }$ ). The left column summarizes the components of the selected jailbreak templates. It visualizes each prompt as a horizontal stacked bar chart, where each bar segment corresponds to a specific component. As shown in Fig. 3A, the bar segments are 

![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_3.jpg)



Fig. 3. The visual design of (A) prompt components and (B) three types of component perturbation strategies.


![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_4.jpg)



Fig. 4. (A) The importance and performance of the keyword. (B) The encoding scheme for the keyword. (C) The alternative design.


arranged in the order corresponding to the prompt components, with the color encoding the component type and the length indicating the token length. It helps users understand the general patterns of prompt components and serves as the baseline for prompt perturbation. Users can click the icon $\textcircled{9}$ to view the template details in the Instance View and click the icon $\mathcal { Y }$ to generate a set of component perturbation results for comparative analysis. 

For comparison, the perturbation results are visualized in the right column as horizontal stacked bars similar to the original templates. Each result is generated by applying a perturbation strategy to a component of the original template. To visualize this difference, we design three kinds of glyphs to represent these strategies and overlay them on the corresponding bar segments, as shown in Fig. $3 B$ . The system also automatically evaluates the jailbreak performance of these perturbation results based on the selected questions and visualizes the percentage of assessment results in pie charts, enabling users to compare the effects of different component perturbations. Users can toggle to check the perturbation results of a particular strategy using the radio box at the top of the column. 

# E. Keyword Exploration

The Keyword View (Fig. $2 D$ ) visualizes the jailbreak performance and importance of keywords (Section IV-C). Specifically, as shown in Fig. 4A, the jailbreak performance of keyword $k$ , i.e., performance $( k )$ , is represented as the percentage of four categories of assessment results, denoted as $[ n _ { 1 } , n _ { 2 } , n _ { 3 } , n _ { 4 } ]$ . Inspired by prior work [64], we introduce a square space with a coordinate system (Fig. $4 B$ ) whose four vertices correspond to the four categories, and their coordinates are denoted as $[ c _ { 1 } , c _ { 2 } , c _ { 3 } , c _ { 4 } ]$ . Each corner is colored to indicate its category. To visualize the overall performance distribution of the keyword, the coordinate of the keyword $k$ is computed as: coor $\begin{array} { r } { d i n a t e ( k ) = \sum _ { i = 1 } ^ { 4 } n _ { i } \times c _ { i } } \end{array}$ . Besides, the size of the keywords encodes their importance in the corpus. To address keyword overlapping, the view prioritizes 

keeping the more important keywords and tries to make slight positional shifts to the less important ones. The position shifts need to be as small as possible and maintain the relative proximity of the keyword to the four vertices (e.g., closer to Full Refusal). Otherwise, we remove the less important keywords. During keyword exploration, users can filter keywords by component type and click the keywords to view their context. 

Alternative Design: We have also considered an alternative design (Fig. 4C) where the keywords are visualized in four separate word clouds (each for one assessment category) and their sizes correspond to their importance to the prompts of this category, i.e., importance(k) × ni, i ∈ [1, 4]. According to the feedback from the experts, although this design enables users to focus on the keywords in the same category, it is inefficient for users to compare the size of the same keywords in different word clouds to estimate their overall performance distribution. Therefore, we chose our current design. 

# F. Template Instance Refinement

The Instance View (Fig. $2 E$ ) allows users to refine the templates and evaluate the performance. The Jailbreak Content panel (Fig. $2 E _ { 1 }$ ) lists the prompt text of each component, which supports manual modifications or automatic perturbations. Users can click the icon at the right of the component title to delete, rephrase, or switch the components. Then, users can evaluate their jailbreak performance on the selected questions and inspect the evaluation results in the Jailbreak Results panel (Fig. $2 E _ { 2 }$ ). Each result item shows the question and model response and visualizes the color of the assessment result. This feedback can help the user evaluate the effectiveness of the modifications to verify the findings during the component and keyword analysis. 

# VI. EVALUATION

We conducted a case study, two technical evaluations, and expert interviews to evaluate the system. We have obtained users’ consent to analyze their exploration process. 

# A. Case Study

We invited the experts mentioned in Section III-B to use our system for jailbreak prompt analysis according to their exploratory interests. In this case study, the expert (E3) first evaluated the overall defense performance of GPT-3.5 on a jailbreak corpus and then dived into multiple prompt categories for an in-depth analysis of prompt characteristics. 

Jailbreak Performance Evaluation (Fig. 5A): E3 uploaded a jailbreak prompt corpus in the Configuration View and selected some questions and templates for analysis. Considering the stochastic nature of model responses, E3 evaluated three responses for each question and template combination. The left part of Summary View visualized the jailbreak performance in pie charts (Fig. $5 A _ { 1 }$ ). Noticing low self-consistency in the results of the Adult Content questions (e.g., ADULT(2)), E3 explored them to verify correctness in the Response View (Fig. $5 A _ { 2 - 1 }$ ). From the scatterplot, he observed some blue outliers located 

![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_5.jpg)


![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_6.jpg)



Fig. 5. The case study. (A) The expert evaluated the performance of the jailbreak prompts and explored the assessment results (e.g., ADULT(2)) to correct unexpected results and refine the assessment criteria. (B) The expert analyzed the Subject Characteristic components in Character Role Play templates and identified important keywords, such as “disregards” and “controversial”. (C) Finally, the expert refined a weak jailbreak prompt based on these keywords and the results verified the effectiveness of these keywords in improving jailbreak performance.


in the red clusters, from which he identified some unexpected assessment results. After correcting an unexpected result (Fig. $5 A _ { 2 - 2 } )$ ) and specifying additional assessment criteria in natural language, the Summary View and Response View (Fig. $5 A _ { 2 - 3 } \mathrm { { \Omega } }$ were updated accordingly. He also explored some other questions to verify their correctness or correct unexpected results. Based on the verified evaluation results (Fig. $5 A _ { 3 } \mathrm { { \ : } }$ ), E3 found that more than half of the jailbreak attacks were successful, indicating the target model was vulnerable ( ). Besides, he also noticed that jailbreak performance usually depended more on templates than questions ( ) because the pie charts in the same row (corresponding to the same templates with different questions) usually showed similar patterns of the percentages of assessment results. 

Prompt Characteristic Exploration (Fig. 5B): E3 was interested in the Character Role Play category, one of the most common categories. The component visualizations (Fig. $5 B _ { 1 - 1 }$ ) showed that Subject Characteristic (SC) components were commonly used and could occupy a large portion of the prompt length ( ). To investigate whether they were important to jailbreak performance, E3 performed component perturbation on strong templates for comparative analysis. The results showed that deleting (Fig. $5 B _ { 1 - 2 }$ ) or switching (Fig. $5 B _ { 1 - 3 }$ ) the SC component resulted in a much more significant performance reduction than the other components, suggesting that it was crucial to the prompt performance ( ). E3 also explored some other prompts and got similar findings. Then, he used the Keyword View to deeply explore the keywords in the SC components (Fig. $5 B _ { 2 }$ ). He found “AIM” and “DAN” near the “Full Refusal” corner, indicating that the model has been 

trained to be wary of these well-known strategies ( ). In contrast, keywords like “disregards” and “controversial” were close to the “Full Compliance” corner, suggesting that encouraging the model to disregard legal and ethical constraints and generate controversial content is still effective. 

Jailbreak Template Refinement (Fig. 5C): To verify the effectiveness of these keywords, E3 selected a weak template and used the keywords to refine the SC component (Fig. $5 C _ { 1 - 1 } \mathrm { \stackrel { . } { } }$ ). The evaluation results of this new template (Fig. $5 C _ { 1 - 2 }$ ) showed that more than half of the attacks were successful, suggesting a significant performance improvement. E3 also tested synonyms of these keywords (e.g., “ignores” and “contentious”) and achieved similar improvements. After validations on other templates, E3 concluded that the strategy behind these keywords reflected a potential model weakness ( ). Finally, he added these newly generated templates to the dataset to improve prompt diversity. 

Conclusion: E3 accumulated more findings in the following analysis process. For example, when exploring the Assumed Responsibility templates, E3 found that the Scene Introduction (SI) and Task Operation (TO) components were frequently used and were crucial to jailbreak performance in some cases. From the keywords in SI components, E3 identified a novel strategy of describing the scene as a “diabolical” plan, he also verified its effectiveness on other prompts. In Output Specification (OS) components, requiring model responses to begin with an emoji can surprisingly improve the jailbreak performance. These findings provide valuable insights for enhancing the model’s security. emphasizes the need for security enhancement, while suggests prioritizing the jailbreak templates 


TABLE III THE ASSESSMENT ACCURACY AND AVERAGED REFINEMENT TIME OF OUR METHOD UNDER DIFFERENT CONDITIONS


<table><tr><td>Model</td><td>Assessment Criteria</td><td>Accuracy</td><td>Refinement Time</td></tr><tr><td>GPT-4o</td><td>Default</td><td>77.50%</td><td>-</td></tr><tr><td>Llama 3.1</td><td>Default</td><td>83.00%</td><td>-</td></tr><tr><td>Llama 3.1</td><td>Refined (Tabular UI)</td><td>88.25%</td><td>229.19s</td></tr><tr><td>Llama 3.1</td><td>Refined (Our System)</td><td>92.25%</td><td>123.33s</td></tr></table>

due to their significant contributions to the success of the attacks. Targeting the model’s weaknesses, developers can construct new jailbreak prompts for safety training [12] based on the findings like , and improve the prompt-oriented content moderation [13] according to the findings like . 

# B. Technical Evaluations

Jailbreak result assessment and prompt component classification are critical to the analysis workflow. Therefore, we conducted two technical evaluations to quantitatively measure the effectiveness of our work. Since no recognized benchmark datasets were available for these two tasks, we collaborated with the experts (E1-E4) to build improvised datasets and evaluated our methods. Then, we analyzed the results and reported some failure cases. 

1) Jailbreak Result Assessment: In this task, we gathered model responses triggered by common jailbreak prompts, labeled the model responses, and evaluated the performance of our method with different criteria. 

Dataset: We randomly selected 20 questions from common question categories and 20 templates for each question. Each question-template combination gathered three responses from the target model GPT-3.5 with a temperature of 2.0. After removing common duplicate answers (e.g., “I’m sorry, I can’t assist with that request.”), we randomly selected 50 responses for each question and divided 30 of them into an exploratory set and 20 into an evaluation set. Then, we worked with the experts to manually categorize the model responses. 

Methodology: We used the evaluation sets totaling $2 0 * 2 0 =$ 400 items to measure accuracy. We first compared the accuracy of Llama 3.1 (405B) and GPT-4o using default criteria (Section IV-A2). For the better-performing model, we further evaluated its performance with refined criteria. To simulate realistic scenarios of criteria refinement, we invited experts (E3 and E4) to analyze the assessment results of exploratory sets in 1) a tabular interface (i.e., Microsoft Excel) or 2) our system to provide corrected examples and specify additional criteria. We measure the accuracy of these two conditions on the evaluation sets as well as the task completion time. 

Result: As shown in Table III, with the default criteria, GPT-4o achieved $7 7 . 5 \%$ accuracy and Llama 3.1 achieved $8 3 . 0 \%$ accuracy. Llama 3.1 performed better, but there’s still room for improvement. Then, the experts refined the criteria for Llama under two conditions. Using the tabular interface achieved $8 8 . 2 5 \%$ accuracy in an average of 229.19 seconds, while using our system achieved $9 2 . 2 5 \%$ accuracy in an average of 123.33 seconds. The 

![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_7.jpg)



Fig. 6. The distribution of the assessment accuracy of Llama 3.1 model on different jailbreak questions.



TABLE IV THE CONFUSION MATRIX FOR THE CLASSIFICATION ACCURACY OF GPT-4O ACROSS COMPONENT TYPES


![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_8.jpg)


results indicated that the criteria refinement in both conditions improved the assessment accuracy, especially for Adult Content questions (Fig. 6), whose legality varies in different countries. Moreover, our system achieved higher performance in shorter times compared to the tabular workspace. 

We also analyzed experts’ exploration processes and conducted interviews to gather their feedback. We found that when using the tabular interface, they typically reviewed the results sequentially, thus overlooking the redundancy of similar corrected examples in the refined criteria. This issue was mitigated in our system, as the system helped users comprehensively identify model confusion and correct representative examples for refining criteria, potentially leading to higher accuracy. The experts also noted that our system offered a more user-friendly experience by alleviating the overwhelming and exhausting process of reviewing large amounts of text. 

2) Prompt Component Classification: Based on the prompt component corpus developed in collaboration with the experts (as detailed in Section III-C), we constructed a dataset to evaluate our component classification method. 

Dataset and Methodology: From the corpus, we randomly selected 50 prompts with 841 prompt sentences in total. Then, we employed GPT-4o and Llama 3.1 (405B) to classify each sentence based on the component taxonomy (Table I). Finally, we measured the classification accuracy of these two models. 

Result: Overall, GPT-4o achieved $9 1 . 5 6 \%$ accuracy and Llama achieved $8 8 . 4 7 \%$ accuracy. We also visualize the classification accuracy of the better-performing model (i.e., GPT-4o) in a confusion matrix in Table IV. The model yielded satisfactory performance in most component categories. However, we noticed some confusion between different categories. For example, the model sometimes incorrectly categorized the Scene 

![image](images/MinerU_markdown_JailbreakLens_Visual_Analysis_of_Jailbreak_Attacks_Against_Large_Language_Models_2041432239274975232/figure_9.jpg)



Fig. 7. The questionnaire results in terms of the effectiveness, usability, and design of our system.


Introduction components as Subject Characteristic type. We analyzed these results and found that some of them depicted scenes that could imply the subject characteristics (e.g., a fictional world without moral constraints), potentially leading to confusion in LLM. A possible solution would be to further clarify the component definition and highlight their nuances to reduce model confusion. Moreover, the formulation and annotation of prompt components inevitably introduce some degree of human subjectivity, which may impact the model’s performance. We discuss this in Section VII-C. 

# C. Expert Interview

We interviewed six external experts (E5-E10) to evaluate the analysis framework’s effectiveness and the visual system’s usability. E5 is a model security engineer from a technical company who has been working on the secure reasoning of LLMs for more than one year and on network security (situation awareness) for over three years. E6-E10 are senior researchers from related fields, including model security, trustworthy AI, and deep learning model training. Among them, E7 has accumulated several years of experience in data and model security before focusing on LLM jailbreak attacks. Each expert interview lasted about 90 minutes. We first briefly introduced the background and motivation of our study. Then, we described the analysis framework and visual system and demonstrated the system workflow using the case study. After that, we invited the experts to explore our system to analyze the performance and characteristics of the jailbreak prompts. Finally, the experts filled in a questionnaire with 9 questions (Fig. 7) about the system’s effectiveness, usability, and design. Overall, the experts provided positive feedback about our system in all dimensions. We also interviewed them to collect comments about the analysis framework, visualization and interaction, and improvement suggestions. 

Analysis Framework: All the experts agreed that our framework facilitated jailbreak performance evaluation and prompt characteristic understanding, and its workflow made sense. They praised this framework as it “provided a more comprehensive and systematic evaluation for jailbreak attacks” (E5) and “greatly improved the analysis efficiency” (E7). For the jailbreak 

assessment, E5 appreciated its flexibility in supporting customized criteria for different user values and local regulations. The component analysis was described as “interesting” (E10), “impressive” (E6), and “inspiring” (E7). It was valued for “offering a new perspective to study the prompt patterns in the black box scenarios” (E10) and “guiding user effort towards the critical parts of the prompts” (E9). The experts confirmed that keyword analysis helped understand prompt characteristics, especially the kernel of the jailbreak strategies. E5 suggested that incorporating an external corpus of suspicious keywords could further improve its effectiveness when analyzing only a few prompts. Finally, all experts agreed that our analysis framework provided valuable insights for red-teaming LLMs. The experts mentioned the findings could enhance both sides of adversarial attacks (i.e., LLM and attacker), ultimately strengthening the model security. We discuss these benefits in Section VII-A. 

Visualization and Interactions: Overall, the experts agreed that the system views were well-designed, and the visual design and interaction were intuitive. E5 and E10 liked the Summary View as it supported the analysis and comparison of jailbreak performance from both the question and template perspectives. Most experts appreciated the guidance of self-consistency scores and the helpfulness of Response View in exploring model responses and identifying unexpected results. E7 noted that while component visualization required some learning costs, it was easy to use and remember once she was familiar with visual encoding. We also asked the experts’ opinions about the color scheme of the prompt components, and the experts confirmed that it was “clear” (E8) and “easy to distinguish” (E10). The Keyword View was observed to be frequently used by the experts during the exploration. Some experts reported that it improved the efficiency of exploring the tricks in different prompts and components. 

Suggestions for Improvement: We have also collected some suggestions for improvement. For Response View, E9 suggested adding some textual annotations, such as keywords near the points or clusters, to summarize the semantics of the responses, which could help users identify the potential incorrect assessment results more efficiently. For component analysis, E5 suggested that providing a textual or visual summary for the comparative analysis of the component perturbations could better help users identify effective components. 

# VII. DISCUSSION

In this section, we distill some design implications from expert interviews to inspire future research. We also discuss the system’s generalizability, limitations, and future work. 

# A. Design Implications

Toward a more comprehensive assessment of jailbreak results: The experts appreciate the introduction of jailbreak taxonomy [23] and the LLM-based method to facilitate jailbreak assessment. They also suggest extending them to include more assessment dimensions. For instance, professional advice on illegal activities may pose a greater risk than amateur ones. Therefore, assessing the helpfulness of the jailbreak results can 

help model practitioners prioritize identifying and preventing these harmful results. Future research can explore broadening the spectrum of assessment dimensions to comprehensively analyze and mitigate the harm of jailbreak results. 

Improve learning-based jailbreak prompt construction: While learning-based methods [13], [18] have greatly improved the efficiency of jailbreak prompt construction, they still face challenges regarding effectiveness due to the intricate prompt design [20]. The experts highlight that our analysis framework can inspire the research of learning-based methods (attackers). For example, pairs of jailbreak prompts and their enhanced perturbation variants can be used to train generative models for rewriting jailbreak prompts, so that the models can easily capture their differences and learn how to effectively improve the prompt performance. Furthermore, the component analysis paves the way for integrating expert knowledge into automatic jailbreak prompt generation. It allows the experts to specify the kernel of the prompts (e.g., Subject Characteristic) to guide the generation of the following content. 

Balance the training objectives of safety and instructionfollowing: Safety and instruction-following are usually competitive objectives [12] in LLM training, where over-strengthening the model’s security defenses using large jailbreak corpora will inevitably compromise the instruction-following abilities, leading to “overkill” issues [75]. The experts point out that our component analysis provides a potential solution to balance these two objectives. As it reveals the vulnerabilities of LLMs, users can construct a condensed jailbreak dataset for the model’s major weaknesses rather than relying on large jailbreak corpora. Future visualization research can explore how to help model practitioners analyze and trade-off between these two objectives. 

Support jailbreak performance comparisons on multiple models: While our work contributes to a systematic analysis of jailbreak attacks, the experts express interest in the comparative evaluation between various models, which can benefit several application scenarios. For example, it can help LLM vendors benchmark their models with competitors and identify their advantages and shortcomings. Similarly, it can assist model practitioners in comparing different versions of models to evaluate the effectiveness of the safety training. Our system can be extended with comparative visualizations [76], [77] to provide insightful comparisons across models. 

Dynamic evaluation for evolving LLMs: As LLMs continuously strengthen the model security, adversaries simultaneously advance jailbreak strategies to improve their effectiveness. This dynamic interplay underscores the need for timely and adaptive evaluation of model security. Our system supports user-customized jailbreak corpora, facilitating the incorporation of advanced attack strategies. Users can collect templates based on established security benchmarks [16] (e.g., HarmBench [24]) or reactivation techniques [20] (e.g., rephrasing and nesting), ensuring comprehensive and up-to-date evaluations of LLM security against emerging threats. 

# B. Generalizability

JailbreakLens is designed to analyze jailbreak attacks, one of the most common prompt attacks. We demonstrate the system’s 

effectiveness through a case study evaluating the vulnerability of GPT-3.5. The system can be generalized to other language models (e.g., Llama 2 [3] and ChatGLM [78]) due to its modelagnostic design. Moreover, the analysis workflow of Jailbreak-Lens can potentially support other prompt attack scenarios, such as prompt injection [14], [25] and backdoor attacks [79], [80]. Prompt injection crafts malicious prompts to leak critical information (e.g., initial system prompts). The system can help users specify criteria for assessing information leakage, providing a comprehensive evaluation of injection performance. Backdoor attacks embed hidden triggers (e.g., specific sentences or keywords) into the model during training. The system can help users identify suspicious triggers through component perturbation and keyword analysis. 

# C. Limitations and Future Work

Explain the jailbreak attacks from the internal mechanisms of LLMs: Our work is model-agnostic and focuses on identifying the key factors of jailbreak success at the component and keyword levels. One of our future works is to probe the internal mechanisms of LLMs to explain the jailbreak attacks. Recent studies [81] have indicated that while LLMs can internally distinguish unethical concepts, they fail to associate them with negative emotions due to the disruptions of jailbreak prompts, ultimately leading to jailbroken results. Leveraging visualization tools [34], [35], users can explore the internal states of LLMs (e.g., neuron activation) and identify patterns that emerge when the models encounter attacks. By integrating the findings of effective components and keywords, visualizations can provide deeper insights into how these elements disrupt the internal associations or how LLMs counteract them after security enhancement. 

Mitigate human subjectivity in component classification: We collaborate with experts to analyze prompt characteristics and develop component taxonomy. While this approach benefits from domain expertise, it may inevitably introduce some degree of human subjectivity. To mitigate this, we decompose long text into basic sentences to reduce ambiguity and conduct multi-round discussions to reach consensus. Evaluation results show effectiveness, though some ambiguities remain. We aim to incorporate larger corpora and involve more experts to refine the component taxonomy, which will help better summarize jailbreak strategies and evaluate model vulnerability. 

Incorporate more component perturbation strategies: Our work has supported three kinds of perturbation strategies (i.e., deletion, rephrasing, and switching) to probe the effect of prompt components on jailbreak performance. They can be extended to support more strategies, such as inserting and crossover [23]. The system can insert the identified important components into other prompts or cross components of two prompts to combine their strengths. Supporting these strategies enables a more comprehensive analysis of prompt components. 

Explore multi-modal jailbreak attacks: The vulnerabilities of multi-modal large language models (MLLMs), such as LLava [82] and GPT-4V [83], have attracted increased attention [84], [85], [86]. MLLMs are more sensitive to jailbreak prompts with multi-modal triggers, including textual triggers, 

OCR textual triggers, and visual triggers, which present greater safety risks compared to LLMs. In the future, we aim to bridge this gap by incorporating multi-modal analysis into our analysis framework to enhance the robustness of MLLMs against such threats. 

# VIII. CONCLUSION

We present a novel LLM-assisted analysis framework coupled with a visual analysis system JailbreakLens to help model practitioners analyze the jailbreak attacks against LLMs. The analysis framework provides a jailbreak result assessment method to evaluate jailbreak performance and supports an in-depth analysis of jailbreak prompt characteristics from component and keyword aspects. The visual system allows users to explore the evaluation results, identify important prompt components and keywords, and verify their effectiveness. A case study, two technical evaluations, and expert interviews show the effectiveness of the analysis framework and visual system. Besides, we distill a set of design implications to inspire future research. 

# ACKNOWLEDGMENT

The authors would like to thank the anonymous reviewers for their valuable comments. 

# REFERENCES



[1] L. Ouyang et al., “Training language models to follow instructions with human feedback,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2022, pp. 27730–27744. 





[2] J. Achiam et al., “GPT-4 technical report,” 2024, arXiv:2303.08774. 





[3] H. Touvron et al., “LLaMA: Open and efficient foundation language models,” 2023, arXiv:2302.13971. 





[4] S. Brade, B. Wang, M. Sousa, S. Oore, and T. Grossman, “Promptify: Textto-image generation through interactive prompt exploration with large language models,” in Proc. ACM Symp. User Interface Softw. Technol., 2023, pp. 1–14. 





[5] T. Angert, M. Suzara, J. Han, C. Pondoc, and H. Subramonyam, “Spellburst: A node-based interface for exploratory creative coding with natural language prompts,” in Proc. ACM Symp. User Interface Softw. Technol., 2023, pp. 1–22. 





[6] Z. Peng, X. Wang, Q. Han, J. Zhu, X. Ma, and H. Qu, “Storyfier: Exploring vocabulary learning support with text generation models,” in Proc. ACM Symp. User Interface Softw. Technol., 2023, pp. 1–16. 





[7] Y. Liu, Z. Wen, L. Weng, O. Woodman, Y. Yang, and W. Chen, “SPROUT: Authoring programming tutorials with interactive visualization of large language model generation process,” 2023, arXiv:2312.01801. 





[8] M. X. Liu et al., ““What it wants me to say”: Bridging the abstraction gap between end-user programmers and code-generating large language models,” in Proc. CHI Conf. Hum. Factors Comput. Syst., 2023, pp. 1–31. 





[9] T. Xie et al., “OpenAgents: An open platform for language agents in the wild,” 2023, arXiv:2310.10634. 





[10] L. Weng, X. Wang, J. Lu, Y. Feng, Y. Liu, and W. Chen, “InsightLens: Discovering and exploring insights from conversational contexts in largelanguage-model-powered data analysis,” 2024, arXiv:2404.01644. 





[11] Y. Liu et al., “Jailbreaking ChatGPT via prompt engineering: An empirical study,” 2024, arXiv:2305.13860. 





[12] A. Wei, N. Haghtalab, and J. Steinhardt, “Jailbroken: How does LLM safety training fail,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024, pp. 80079–80110. 





[13] G. Deng et al., “MasterKey: Automated jailbreaking of large language model chatbots,” 2024, arXiv:2307.08715. 





[14] E. Shayegani, M. A. A. Mamun, Y. Fu, P. Zaree, Y. Dong, and N. Abu-Ghazaleh, “Survey of vulnerabilities in large language models revealed by adversarial attacks,” 2023, arXiv:2310.10844. 





[15] P. Chao, A. Robey, E. Dobriban, H. Hassani, G. J. Pappas, and E. Wong, “Jailbreaking black box large language models in twenty queries,” 2023, arXiv:2310.08419. 





[16] J. Chu, Y. Liu, Z. Yang, X. Shen, M. Backes, and Y. Zhang, “Comprehensive assessment of jailbreak attacks against LLMs,” 2024, arXiv:2402.05668. 





[17] X. Shen, Z. Chen, M. Backes, Y. Shen, and Y. Zhang, ““do anything now”: Characterizing and evaluating in-the-wild jailbreak prompts on large language models,” 2023, arXiv:2308.03825. 





[18] A. Zou, Z. Wang, J. Z. Kolter, and M. Fredrikson, “Universal and transferable adversarial attacks on aligned language models,” 2023, arXiv:2307.15043. 





[19] H. Sun, Z. Zhang, J. Deng, J. Cheng, and M. Huang, “Safety assessment of chinese large language models,” 2023, arXiv:2304.10436. 





[20] P. Ding et al., “A wolf in sheep’s clothing: Generalized nested jailbreak prompts can fool large language models easily,” 2024, arXiv:2311.08268. 





[21] X. Liu, N. Xu, M. Chen, and C. Xiao, “AutoDAN: Generating stealthy jailbreak prompts on aligned large language models,” 2024, arXiv:2310.04451. 





[22] H. Jin, R. Chen, J. Chen, and H. Wang, “Quack: Automatic jailbreaking large language models via role-playing,” 2024. [Online]. Available: https: //openreview.net/forum?id=1zt8GWZ9sc 





[23] J. Yu, X. Lin, and X. Xing, “GPTFUZZER: Red teaming large language models with auto-generated jailbreak prompts,” 2023, arXiv:2309.10253. 





[24] M. Mazeika et al., “HarmBench: A standardized evaluation framework for automated red teaming and robust refusal,” 2024, arXiv:2402.04249. 





[25] F. Perez and I. Ribeiro, “Ignore previous prompt: Attack techniques for language models,” 2022, arXiv:2211.09527. 





[26] D. Kang, X. Li, I. Stoica, C. Guestrin, M. Zaharia, and T. Hashimoto, “Exploiting programmatic behavior of LLMs: Dual-use through standard security attacks,” 2023, arXiv:2302.05733. 





[27] Y. Yuan et al., “GPT-4 is too smart to be safe: Stealthy chat with LLMs via cipher,” 2024, arXiv:2308.06463. 





[28] T. Y. Zhuo, Y. Huang, C. Chen, and Z. Xing, “Red teaming ChatGPT via jailbreaking: Bias, robustness, reliability and toxicity,” 2023, arXiv:2301.12867. 





[29] H. Li, D. Guo, W. Fan, M. Xu, and Y. Song, “Multi-step jailbreaking privacy attacks on ChatGPT,” 2023, arXiv:2304.05197. 





[30] X. Chen et al., “Visual analytics for security threats detection in ethereum consensus layer,” J. Visual., vol. 27, no. 3, pp. 469–483, 2024. 





[31] D. Ziegler et al., “Adversarial training for high-stakes reliability,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2022, pp. 9274–9286. 





[32] A. Shafahi et al., “Poison frogs! targeted clean-label poisoning attacks on neural networks,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2018, pp. 6106–6116. 





[33] Y. Liu et al., “Trojaning attack on neural networks,” in Proc. Annu. Netw. Distrib. Syst. Secur. Symp., 2018. [Online]. Available: http://dx.doi.org/ 10.14722/ndss.2018.23291 





[34] M. Liu, S. Liu, H. Su, K. Cao, and J. Zhu, “Analyzing the noise robustness of deep neural networks,” in Proc. 2018 IEEE Conf. Vis. Analytics Sci. Technol., 2018, pp. 60–71. 





[35] N. Das et al., “Bluff: Interactively deciphering adversarial attacks on deep neural networks,” in Proc. IEEE Vis. Conf., 2020, pp. 271–275. 





[36] Y. Ma, T. Xie, J. Li, and R. Maciejewski, “Explaining vulnerabilities to adversarial machine learning through visual analytics,” IEEE Trans. Vis. Comput. Graph., vol. 26, no. 1, pp. 1075–1085, Jan. 2020. 





[37] Z. Jin, S. Liu, H. Li, X. Zhao, and H. Qu, “JailbreakHunter: A visual analytics approach for jailbreak prompts discovery from large-scale human-LLM conversational datasets,” 2024, arXiv:2407.03045. 





[38] D. Deng, C. Zhang, H. Zheng, Y. Pu, S. Ji, and Y. Wu, “AdversaFlow: Visual red teaming for large language models with multi-level adversarial flow,” IEEE Trans. Vis. Comput. Graph., vol. 31, no. 1, pp. 492–502, Jan. 2025. 





[39] A. Karpathy, J. Johnson, and L. Fei-Fei, “Visualizing and understanding recurrent networks,” 2015, arXiv:1506.02078. 





[40] J. Li, X. Chen, E. Hovy, and D. Jurafsky, “Visualizing and understanding neural models in NLP,” 2016, arXiv:1506.01066. 





[41] T. Spinner, U. Schlegel, H. Schäfer, and M. El-Assady, “explAiner: A visual analytics framework for interactive and explainable machine learning,” IEEE Trans. Vis. Comput. Graph., vol. 26, no. 1, pp. 1064–1074, Jan. 2020. 





[42] Y. Feng et al., “XNLI: Explaining and diagnosing NLI-based visual data analysis,” IEEE Trans. Vis. Comput. Graph., vol. 30, no. 7, pp. 3813–3827, Jul. 2024. 





[43] Y. Feng et al., “iPoet: Interactive painting poetry creation with visual multimodal analysis,” J. Visual., vol. 25, pp. 671–685, 2022. 





[44] X. Wang, R. Huang, Z. Jin, T. Fang, and H. Qu, “CommonsenseVIS: Visualizing and understanding commonsense reasoning capabilities of natural language models,” IEEE Trans. Vis. Comput. Graph., vol. 30, no. 1, pp. 273–283, Jan. 2024. 





[45] F. Cheng, Y. Ming, and H. Qu, “DECE: Decision explorer with counterfactual explanations for machine learning models,” IEEE Trans. Vis. Comput. Graph., vol. 27, no. 2, pp. 1438–1447, Feb. 2021. 





[46] Y. Ming et al., “Understanding hidden memories of recurrent neural networks,” in Proc. IEEE Conf. Vis. Analytics Sci. Technol., 2017, pp. 13–24. 





[47] H. Strobelt, S. Gehrmann, H. Pfister, and A. M. Rush, “LSTMVis: A tool for visual analysis of hidden state dynamics in recurrent neural networks,” IEEE Trans. Vis. Comput. Graph., vol. 24, no. 1, pp. 667–676, Jan. 2018. 





[48] A. Vaswani et al., “Attention is all you need,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2017, pp. 6000–6010. 





[49] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training of deep bidirectional transformers for language understanding,” 2018, arXiv: 1810.04805. 





[50] C. Yeh, Y. Chen, A. Wu, C. Chen, F. Viégas, and M. Wattenberg, “AttentionViz: A global view of transformer attention,” IEEE Trans. Vis. Comput. Graph., vol. 30, no. 1, pp. 262–272, Jan. 2024. 





[51] Z. Shao et al., “Visual explanation for open-domain question answering with BERT,” IEEE Trans. Vis. Comput. Graph., vol. 30, no. 7, pp. 3779–3797, Jul. 2024. 





[52] L. Gao, Z. Shao, Z. Luo, H. Hu, C. Turkay, and S. Chen, “TransforLearn: Interactive visual tutorial for the transformer model,” IEEE Trans. Vis. Comput. Graph., vol. 30, no. 1, pp. 891–901, Jan. 2024. 





[53] A. Boggust, B. Hoover, A. Satyanarayan, and H. Strobelt, “Shared interest: Measuring human-ai alignment to identify recurring patterns in model behavior,” in Proc. CHI Conf. Hum. Factors Comput. Syst., 2022, pp. 1–17. 





[54] N. Feldhus, A. M. Ravichandran, and S. Möller, “Mediators: Conversational agents explaining NLP model behavior,” 2022, arXiv:2206.06029. 





[55] P. P. Liang et al., “MultiViz: Towards visualizing and understanding multimodal models,” 2022, arXiv:2207.00056. 





[56] Y. Feng et al., “PromptMagician: Interactive prompt engineering for text-to-image creation,” IEEE Trans. Vis. Comput. Graph., vol. 30, no. 1, pp. 295–305, Jan. 2024. 





[57] Z. Li et al., “A unified understanding of deep NLP models for text classification,” IEEE Trans. Vis. Comput. Graph., vol. 28, no. 12, pp. 4980–4994, Dec. 2022. 





[58] H. Strobelt et al., “Interactive and visual prompt engineering for ad-hoc task adaptation with large language models,” IEEE Trans. Vis. Comput. Graph., vol. 29, no. 1, pp. 1146–1156, Jan. 2023. 





[59] L. Weng et al., “Towards an understanding and explanation for mixedinitiative artificial scientific text detection,” 2023, arXiv:2304.05011. 





[60] P. Jiang, J. Rayan, S. P. Dow, and H. Xia, “Graphologue: Exploring large language model responses with interactive diagrams,” in Proc. ACM Symp. User Interface Softw. Technol., 2023, pp. 1–20. 





[61] S. Suh, B. Min, S. Palani, and H. Xia, “Sensecape: Enabling multilevel exploration and sensemaking with large language models,” in Proc. ACM Symp. User Interface Softw. Technol., 2023, pp. 1–18. 





[62] J. Lu et al., “AgentLens: Visual analysis for agent behaviors in LLM-based autonomous systems,” 2024, arXiv:2402.08995. 





[63] J. Wexler, M. Pushkarna, T. Bolukbasi, M. Wattenberg, F. Viégas, and J. Wilson, “The what-if tool: Interactive probing of machine learning models,” IEEE Trans. Vis. Comput. Graph., vol. 26, no. 1, pp. 56–65, Jan. 2020. 





[64] S. Liu, Z. Li, T. Li, V. Srikumar, V. Pascucci, and P.-T. Bremer, “NLIZE: A perturbation-driven visual interrogation tool for analyzing and interpreting natural language inference models,” IEEE Trans. Vis. Comput. Graph., vol. 25, no. 1, pp. 651–660, Jan. 2019. 





[65] S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting model predictions,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2017, pp. 4765– 4774. 





[66] R. Speer, J. Chin, and C. Havasi, “ConceptNet 5.5: An open multilingual graph of general knowledge,” in Proc. AAAI Conf. Artif. Intell., 2017, pp. 4444–4451. 





[67] Website JailbreakChat, 2023, Accessed: Oct. 01, 2023. [Online]. Available: http://jailbreakchat.com/ 





[68] OpenAI’s usage policies, 2023, Accessed: Oct. 01, 2023. [Online]. Available: https://openai.com/policies/usage-policies 





[69] X. Wang et al., “Self-consistency improves chain of thought reasoning in language models,” 2022, arXiv:2203.11171. 





[70] S. Yao et al., “Tree of thoughts: Deliberate problem solving with large language models,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024, pp. 11809–11822. 





[71] M. T. Ribeiro, T. Wu, C. Guestrin, and S. Singh, “Beyond accuracy: Behavioral testing of NLP models with checklist,” 2020, arXiv: 2005.04118. 





[72] F. Cheng, V. Zouhar, R. S. M. Chan, D. Fürst, H. Strobelt, and M. El-Assady, “Interactive analysis of LLMs using meaningful counterfactuals,” 2024, arXiv:2405.00708. 





[73] K. S. Jones, “A statistical interpretation of term specificity and its application in retrieval,” J. Documentation, vol. 60, no. 5, pp. 493–502, 2004. 





[74] OpenAI’s embedding models, 2023, Accessed: Mar. 01, 2024. [Online]. Available: https://platform.openai.com/docs/guides/embeddings 





[75] C. Shi et al., “Navigating the OverKill in large language models,” 2024, arXiv:2401.17633. 





[76] M. M. Malik, C. Heinzl, and M. E. Groeller, “Comparative visualization for parameter studies of dataset series,” IEEE Trans. Vis. Comput. Graph., vol. 16, no. 5, pp. 829–840, Sep./Oct. 2010. 





[77] W. He, J. Wang, H. Guo, H.-W. Shen, and T. Peterka, “CECAV-DNN: Collective ensemble comparison and visualization using deep neural networks,” Vis. Informat., vol. 4, no. 2, pp. 109–121, 2020. 





[78] Z. Du et al., “GLM: General language model pretraining with autoregressive blank infilling,” 2021, arXiv::2103.10360. 





[79] H. Huang, Z. Zhao, M. Backes, Y. Shen, and Y. Zhang, “Composite backdoor attacks against large language models,” 2023, arXiv:2310.07676. 





[80] W. Yang, X. Bi, Y. Lin, S. Chen, J. Zhou, and X. Sun, “Watch out for your agents! Investigating backdoor threats to LLM-based agents,” 2024, arXiv:2402.11208. 





[81] Z. Zhou, H. Yu, X. Zhang, R. Xu, F. Huang, and Y. Li, “How alignment and jailbreak work: Explain LLM safety through intermediate hidden states,” 2024, arXiv:2406.05644. 





[82] H. Liu, C. Li, Q. Wu, and Y. J. Lee, “Visual instruction tuning,” in Proc. Int. Conf. Neural Inf. Process. Syst., Curran Associates, Inc., 2023, pp. 34892–34916. 





[83] GPT-4V(ision) system card, 2023, Accessed: Mar. 01, 2024. [Online]. Available: https://openai.com/research/gpt-4v-system-card 





[84] N. Carlini et al., “Are aligned neural networks adversarially aligned,” in Proc. Int. Conf. Neural Inf. Process. Syst., Curran Associates, Inc., 2023, pp. 61478–61500. 





[85] E. Shayegani, Y. Dong, and N. Abu-Ghazaleh, “Jailbreak in pieces: Compositional adversarial attacks on multi-modal language models,” in Proc. Int. Conf. Learn. Representations, 2024. 





[86] X. Qi, K. Huang, A. Panda, P. Henderson, M. Wang, and P. Mittal, “Visual adversarial examples jailbreak aligned large language models,” in Proc. AAAI Conf. Artif. Intell., 2024, pp. 21527–21536. 



Yingchaojie Feng is currently working toward the PhD degree with the College of Computer Science and Technology, Zhejiang University, China. His research interests include natural language processing and visual analysis. 

Zhizhang Chen received the BS degree in computer science and technology from Hangzhou Dianzi University, China, in 2022. He is currently working toward the master’s degree with the School of Computer Science, Zhejiang University. His research interests include information visualization and visual analysis. 

Zhining Kang is currently working toward the undergraduate degree with the College of Computer Science and Technology, Zhejiang University. His research interests include information visualization and visual analysis. 

Sijia Wang received the MS degree in software engineering from Zhejiang University, China, in 2024. She is currently working with Alibaba Group, Hangzhou, China. Her research interests include digital humanities, visualization, and visual analytics. 

Minfeng Zhu received the PhD degree in computer science from the State Key Laboratory of CAD&CG, Zhejiang University, in 2020. He is a tenure-track assistant professor with the School of Software Technology, Zhejiang University. His research interests include artificial intelligence and visual analysis. For more information, please visit: https://minfengzhu.github.io 

Haoyu Tian received the BS degree in engineering mechanics from the Huazhong University of Science and Technology, China. He is now working toward the master’s degree with the College of Computer Science and Technology, Zhejiang University. His research interests focus on information visualization, visual analytics, and human-computer interaction. 

Wei Chen is a professor with the State Key Lab of CAD&CG, Zhejiang University. His current research interests include visualization and visual analytics. He has published more than 100 IEEE/ACM Transactions and IEEE VIS papers. He actively served in many leading conferences and journals, like IEEE PacificVIS steering committee, ChinaVIS steering committee, paper co-chairs of IEEE VIS, IEEE PacificVIS, IEEE LDAV and ACM SIGGRAPH Asia VisSym. He is an associate editor of IEEE Transactions on Visualization and Computer Graphics, IEEE Transactions on Big Data, ACM Transactions on Intelligent Systems and Technology, IEEE Transactions on Systems, Man, and Cybernetics: Systems, IEEE Transactions on Intelligent Vehicles, IEEE Computer Graphics and Applications, Frontiers of Computer Science, and Journal of Visualization. More information can be found at: http://www.cad.zju.edu.cn/home/chenwei. 

Wei Zhang received the PhD degree in design science from the State Key Laboratory of CAD&CG, Zhejiang University, in 2025. Her current research interests include digital humanities visualization and visual analytics. 