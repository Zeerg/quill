# Quill Sub-Agents Documentation

This directory contains specialized Claude Code sub-agents designed to assist with different aspects of the Quill LLM fuzzing project. Each agent has specific expertise and can be invoked to help with particular tasks.

## Available Sub-Agents

### Core Fuzzing Agents

#### 1. 🧬 mutator-developer
**Purpose**: Expert in developing and testing mutation strategies for adversarial prompt generation

**Key Capabilities**:
- Design new mutation strategies
- Implement mutator classes following established patterns
- Analyze mutation effectiveness
- Test against multiple LLM models

**Example Usage**:
```
/agent mutator-developer create a new mutation strategy that uses metaphorical encoding to bypass safety filters
```

#### 2. 📊 corpus-analyzer
**Purpose**: Specialist in analyzing prompt corpora and optimizing test coverage

**Key Capabilities**:
- Evaluate corpus diversity and coverage
- Identify gaps in test scenarios
- Organize prompts by category and risk level
- Generate corpus quality metrics

**Example Usage**:
```
/agent corpus-analyzer analyze the current test corpus and identify missing attack categories
```

#### 3. 🔍 results-investigator
**Purpose**: Expert in analyzing fuzzing results and identifying patterns

**Key Capabilities**:
- Deep analysis of fuzzing outputs
- Pattern recognition in model responses
- Anomaly classification and severity assessment
- Statistical analysis of results

**Example Usage**:
```
/agent results-investigator analyze the latest fuzzing run and identify the most effective mutation strategies
```

#### 4. 🛡️ security-auditor
**Purpose**: Security expert for comprehensive LLM safety assessment

**Key Capabilities**:
- Conduct security audits of LLM models
- Create vulnerability reports with CVSS scoring
- Provide remediation recommendations
- Ensure compliance with security standards

**Example Usage**:
```
/agent security-auditor generate a comprehensive security audit report for the latest test campaign
```

#### 5. ⚡ performance-optimizer
**Purpose**: Expert in optimizing fuzzing performance and scalability

**Key Capabilities**:
- Profile and identify performance bottlenecks
- Implement parallel processing strategies
- Optimize resource usage
- Design distributed fuzzing architectures

**Example Usage**:
```
/agent performance-optimizer optimize the fuzzer to handle 10,000 prompts per hour
```

### AI Classifier Agents

#### 6. 🤖 classifier-architect
**Purpose**: Expert in designing and implementing AI classifiers for LLM output analysis

**Key Capabilities**:
- Design BERT/RoBERTa/DistilBERT classifiers
- Implement multi-task and ensemble models
- Create training pipelines
- Optimize model architectures

**Example Usage**:
```
/agent classifier-architect design a multi-label classifier to categorize LLM responses by safety and quality
```

#### 7. 📚 dataset-curator
**Purpose**: Expert in curating and managing datasets for classifier training

**Key Capabilities**:
- Design labeling schemas and taxonomies
- Manage annotation workflows
- Ensure dataset quality and balance
- Create train/val/test splits

**Example Usage**:
```
/agent dataset-curator create a balanced dataset from our fuzzing results for training a safety classifier
```

#### 8. 🏋️ model-trainer
**Purpose**: Expert in training and fine-tuning transformer models

**Key Capabilities**:
- Implement advanced training techniques
- Hyperparameter optimization
- Multi-task and few-shot learning
- Model compression and optimization

**Example Usage**:
```
/agent model-trainer fine-tune a BERT model on our labeled dataset with optimal hyperparameters
```

#### 9. 🚀 inference-optimizer
**Purpose**: Expert in optimizing classifier inference for production

**Key Capabilities**:
- Design high-performance inference pipelines
- Implement caching and batching strategies
- GPU optimization and edge deployment
- Real-time classification systems

**Example Usage**:
```
/agent inference-optimizer create a real-time classification system that can process 1000 responses per second
```

## How to Use Sub-Agents

1. **Direct Invocation**: Use `/agent [agent-name]` followed by your request
2. **Automatic Selection**: Claude Code will automatically select the appropriate agent based on your task
3. **Chaining**: Combine multiple agents for complex workflows

## Example Workflows

### Complete Security Assessment
```
1. /agent corpus-analyzer evaluate test coverage
2. /agent mutator-developer create missing test strategies  
3. Run fuzzing campaign
4. /agent results-investigator analyze findings
5. /agent security-auditor generate audit report
```

### Performance Optimization
```
1. /agent performance-optimizer profile current implementation
2. Implement suggested optimizations
3. /agent performance-optimizer verify improvements
```

### New Feature Development
```
1. /agent mutator-developer design new mutation strategy
2. /agent corpus-analyzer suggest test cases
3. /agent performance-optimizer ensure scalability
```

## Best Practices

1. **Use the Right Agent**: Each agent is specialized - choose based on your specific need
2. **Provide Context**: Give agents relevant context about your current work
3. **Iterate**: Use agents iteratively to refine and improve results
4. **Combine Expertise**: Leverage multiple agents for comprehensive solutions

## Adding New Sub-Agents

To create a new sub-agent:

1. Create a new markdown file in `.claude/agents/`
2. Include frontmatter with name, description, and tools
3. Write a detailed system prompt explaining the agent's role
4. Document specific capabilities and workflows

Example structure:
```markdown
---
name: agent-name
description: Brief description of agent's purpose
tools: List, Of, Allowed, Tools
---

Detailed system prompt explaining role, responsibilities, and approach...
```

## Maintenance

- Regularly update agent prompts based on new findings
- Add new agents as the project evolves
- Remove or merge redundant agents
- Keep agent documentation current

For more information about Claude Code sub-agents, see: https://docs.anthropic.com/en/docs/claude-code/sub-agents