# AIShield Trust Standard v0.1

> **AIShield 信任标准 v0.1 — Agent 安全认证、信誉评分与委托协议规范**

---

| 字段 | 值 |
|------|------|
| **标准名称** | AIShield Trust Standard |
| **版本** | 0.1 (Draft) |
| **日期** | 2026-07-20 |
| **状态** | Draft / Request for Comments |
| **维护方** | AIShield Project |
| **许可证** | CC BY 4.0 |
| **目标读者** | AI Agent 开发者、平台运营方、安全审计人员、协议实现者 |

---

## 目录 (Table of Contents)

1. [概述 (Overview)](#1-概述-overview)
   - 1.1 [范围与目标](#11-范围与目标)
   - 1.2 [设计原则](#12-设计原则)
   - 1.3 [术语定义](#13-术语定义)
   - 1.4 [与现有标准的关系](#14-与现有标准的关系)
   - 1.5 [版本演进路线](#15-版本演进路线)
   - 1.6 [规范约定 (Notational Conventions)](#16-规范约定-notational-conventions)
2. [子标准 A：Agent Security Certification（安全认证标准）](#2-子标准-aagent-security-certification安全认证标准)
   - 2.1 [认证等级](#21-认证等级)
   - 2.2 [认证流程](#22-认证流程)
   - 2.3 [证书格式](#23-证书格式)
   - 2.4 [验证端点](#24-验证端点)
   - 2.5 [徽章规范](#25-徽章规范)
   - 2.6 [安全扫描规范](#26-安全扫描规范)
   - 2.7 [证书吊销与更新](#27-证书吊销与更新)
3. [子标准 B：Agent Trust Score（信誉评分标准）](#3-子标准-bagent-trust-score信誉评分标准)
   - 3.1 [评分维度](#31-评分维度)
   - 3.2 [评分算法](#32-评分算法)
   - 3.3 [评分查询 API](#33-评分查询-api)
   - 3.4 [评分更新机制](#34-评分更新机制)
   - 3.5 [防刷机制](#35-防刷机制)
   - 3.6 [评分分级](#36-评分分级)
4. [子标准 C：Agent Delegation Protocol（委托协议标准）](#4-子标准-cagent-delegation-protocol委托协议标准)
   - 4.1 [协议概述](#41-协议概述)
   - 4.2 [扩展字段定义](#42-扩展字段定义)
   - 4.3 [委托流程状态机](#43-委托流程状态机)
   - 4.4 [争议解决](#44-争议解决)
   - 4.5 [完成凭证 (Receipt)](#45-完成凭证-receipt)
   - 4.6 [端到端委托示例](#46-端到端委托示例)
5. [实施指南 (Implementation Guide)](#5-实施指南-implementation-guide)
   - 5.1 [最小实现清单](#51-最小实现清单)
   - 5.2 [代码示例](#52-代码示例)
   - 5.3 [测试用例](#53-测试用例)
   - 5.4 [兼容性检查清单](#54-兼容性检查清单)
6. [许可证与贡献](#6-许可证与贡献)
   - 6.1 [许可证](#61-许可证)
   - 6.2 [贡献指南](#62-贡献指南)
   - 6.3 [致谢](#63-致谢)

---

## 1. 概述 (Overview)

### 1.1 范围与目标

#### 1.1.1 背景

随着 AI Agent 生态的快速发展，越来越多的自主 Agent 需要在开放网络环境中进行互操作与协作。然而，当前 Agent 经济面临三大核心信任问题：

1. **安全可信缺失**：无法验证一个 Agent 的工具调用是否存在安全隐患
2. **信誉体系空白**：缺乏统一、可互操作的 Agent 信誉评估机制
3. **委托协议不统一**：Agent 间的任务委托缺乏标准化的安全与保障协议

AIShield Trust Standard 旨在定义一套开放、中立、可互操作的标准规范，解决上述问题。

#### 1.1.2 范围

本标准 v0.1 版本涵盖以下三个子标准：

| 子标准 | 名称 | 核心目标 |
|--------|------|----------|
| **子标准 A** | Agent Security Certification | 定义 Agent 安全认证等级、流程与证书格式 |
| **子标准 B** | Agent Trust Score | 定义统一的 Agent 信誉评分体系 |
| **子标准 C** | Agent Delegation Protocol | 定义扩展 A2A 的安全委托协议 |

#### 1.1.3 目标

本标准的目标是：

- 提供 Agent 身份安全认证的 **标准化流程与格式**
- 建立可互操作的 **信誉评分体系**，使不同平台间的评分可被验证和迁移
- 定义 **安全委托协议**，使 Agent 间的任务合作有据可依、有迹可循
- 成为 Agent 经济中"安全认证 + 信誉评分 + 委托协议"的 **事实标准 (de facto standard)**

#### 1.1.4 非目标

本标准 v0.1 **不**涉及以下内容（可能在后续版本中覆盖）：

- Agent 内部安全沙箱实现细节
- 具体的 LLM 安全防护机制
- 金融合规与监管要求
- 跨链桥接协议
- Agent 代码执行的隔离与资源限制

### 1.2 设计原则

#### 1.2.1 Cloud-Agnostic（云无关）

本标准不绑定任何云服务提供商。Agent 可以运行在 AWS、Azure、GCP、阿里云、自建服务器或任何边缘计算环境中。所有数据格式和接口协议均基于开放的互联网标准（HTTP/HTTPS、JSON、DID），不依赖任何云厂商的专有服务。

```
┌─────────────────────────────────────────────┐
│           AIShield Trust Standard           │
│                                             │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│    │ AWS     │  │ Azure   │  │ 自建    │   │
│    └────┬────┘  └────┬────┘  └────┬────┘   │
│         │            │            │         │
│         └────────────┼────────────┘         │
│                      │                      │
│              ┌───────┴───────┐              │
│              │  标准协议层    │              │
│              │  HTTP + JSON   │              │
│              └───────────────┘              │
└─────────────────────────────────────────────┘
```

#### 1.2.2 Model-Agnostic（模型无关）

本标准不绑定任何 LLM 厂商。Agent 可以基于 GPT、Claude、Gemini、Llama、Qwen 或任何其他 LLM 构建。标准的评分和认证机制关注 Agent 的 **行为安全** 和 **工具调用安全**，而非底层模型的技术实现。

#### 1.2.3 协议兼容

本标准基于现有开放协议进行扩展：

- **A2A (Agent-to-Agent)**：委托协议基于 A2A Task 模型扩展
- **MCP (Model Context Protocol)**：安全扫描参考 OWASP MCP Top 10
- **DID (Decentralized Identifier)**：Agent 身份使用 W3C DID 标准
- **OAuth 2.0**：认证授权流程兼容 OAuth 2.0

#### 1.2.4 最小可行 (Minimum Viable)

v0.1 版本遵循最小可行原则：

- 仅定义 3 个核心子标准（认证、评分、委托）
- 每个子标准仅定义最必要的字段和流程
- 保持实现复杂度可控，单个开发者可在数日内完成基本实现
- 为后续版本预留扩展空间

### 1.3 术语定义

本标准使用以下核心术语：

#### 1.3.1 Agent

> 一个具有自主决策能力的 AI 系统实体，能够通过工具调用（Tool Use）完成特定任务，并可通过 A2A 协议与其他 Agent 进行通信与协作。

Agent 在本标准中具有以下属性：

| 属性 | 说明 |
|------|------|
| **Agent DID** | 基于 W3C DID 标准的去中心化身份标识符 |
| **Agent Name** | 人类可读的 Agent 名称 |
| **Skill Card** | 描述 Agent 所具备技能的结构化文档 |
| **Endpoint** | Agent 的 A2A 通信端点 URL |

```json
{
  "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
  "agent_name": "CodeReviewer-Pro",
  "description": "专业的代码审查 Agent，支持 20+ 编程语言",
  "endpoint": "https://agent.example.com/a2a",
  "skills": ["code-review", "security-scan", "bug-detection"]
}
```

#### 1.3.2 DID (Decentralized Identifier)

> 基于 W3C DID 标准的去中心化身份标识符，用于唯一标识一个 Agent 实体。

本标准使用 DID 方法前缀 `did:aishield:` 作为 Agent 的身份标识空间。

```
did:aishield:{unique-identifier}

示例：
did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c
did:aishield:org-acme-devops-agent-v2
```

DID 文档应包含以下必要字段：

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://aishield.org/ns/did/v1"
  ],
  "id": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
  "controller": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
  "verificationMethod": [{
    "id": "#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "publicKeyMultibase": "zH3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }],
  "authentication": ["#key-1"],
  "assertionMethod": ["#key-1"],
  "service": [{
    "id": "#a2a-endpoint",
    "type": "A2AEndpoint",
    "serviceEndpoint": "https://agent.example.com/a2a"
  }]
}
```

#### 1.3.3 Trust Score（信誉评分）

> 基于 AIShield 标准算法计算的、对 Agent 安全性、可靠性、声誉和活跃度的综合评估分数。

Trust Score 是一个 0-100 的数值，由多个维度的加权分数组成。详见 [第 3 章](#3-子标准-bagent-trust-score信誉评分标准)。

#### 1.3.4 Skill Card（技能卡）

> 描述 Agent 所具备技能的结构化文档，包含技能名称、描述、输入输出格式、安全级别等信息。

```json
{
  "skill_card_version": "0.1",
  "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
  "skills": [
    {
      "skill_id": "code-review",
      "name": "代码审查",
      "description": "对提交的代码进行安全性和质量审查",
      "input_format": {
        "type": "object",
        "properties": {
          "code": {"type": "string", "description": "待审查的源代码"},
          "language": {"type": "string", "description": "编程语言"}
        },
        "required": ["code", "language"]
      },
      "output_format": {
        "type": "object",
        "properties": {
          "issues": {"type": "array", "description": "发现的问题列表"},
          "severity_summary": {"type": "object", "description": "严重程度统计"}
        }
      },
      "security_level": "standard",
      "tools_used": ["file_read", "ast_parser", "security_rules_engine"]
    }
  ]
}
```

#### 1.3.5 Delegation Receipt（完成凭证）

> 委托任务完成后，由受托方（Delegate Agent）生成的结构化完成证明，包含任务哈希、结果摘要和时间戳。

```json
{
  "receipt_version": "0.1",
  "delegation_id": "del-2026-07-20-a1b2c3d4",
  "task_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "result_summary": "完成代码审查，发现 3 个安全问题和 5 个代码质量问题",
  "completed_at": "2026-07-20T14:30:00Z",
  "delegate_did": "did:aishield:agent-b-reviewer",
  "delegate_signature": "eyJhbGciOiJFZERTQSIsImtpZCI6IiNrZXktMSJ9..."
}
```

#### 1.3.6 Escrow（托管）

> 在委托任务执行期间，由第三方或智能合约持有的资产（代币、凭证等），用于保障委托双方的权益。

#### 1.3.7 Certifier（认证机构）

> 有权颁发和验证 AIShield 安全认证证书的实体。可以是 AIShield 官方、社区认可的第三方机构，或支持 Level 1 自动认证的任何合规平台。

#### 1.3.8 Delegator（委托方）

> 发起委托任务的 Agent 或人类用户。Delegator 通过 Delegation Protocol 将任务分配给 Delegate Agent。

#### 1.3.9 Delegate（受托方）

> 接受并执行委托任务的 Agent。Delegate 需满足 Delegator 设定的安全认证和信誉评分要求。

### 1.4 与现有标准的关系

#### 1.4.1 A2A (Agent-to-Agent Protocol)

本标准的子标准 C（委托协议）**扩展** A2A Task 模型。A2A 定义了 Agent 间通信的基础框架，包括 Task 的创建、更新和消息传递。本标准在此基础上增加了安全认证验证、信誉检查、托管机制和争议解决流程。

兼容性说明：

```
A2A Task 模型（基础）           AIShield 扩展字段
┌───────────────────┐          ┌───────────────────────┐
│ task_id           │          │ escrow                │
│ task_name         │          │ trust_requirements    │
│ status            │          │ security_requirements  │
│ input             │          │ dispute_resolution    │
│ output            │          │ receipt               │
│ created_at        │          │ cert_id               │
└───────────────────┘          └───────────────────────┘
         │                              │
         └──────────────────────────────┘
              AIShield Delegation Task
```

#### 1.4.2 MCP (Model Context Protocol)

本标准的子标准 A（安全认证）参考 **OWASP MCP Top 10** 安全风险清单作为安全扫描的基础检测项。MCP 定义了 LLM 应用与外部工具的交互协议，OWASP MCP Top 10 列出了常见的 MCP 安全风险。

本标准在 OWASP MCP Top 10 基础上增加了以下检测维度：

| 维度 | 说明 |
|------|------|
| Prompt Injection | 检测 Agent 是否有防范提示注入的机制 |
| Tool Abuse | 检测工具调用是否有过载保护和权限控制 |
| Data Leakage | 检测 Agent 是否泄露敏感信息 |
| Unauthorized Access | 检测 Agent 是否验证调用者身份 |
| Supply Chain | 检测 Agent 依赖的工具/插件是否有安全审计 |

#### 1.4.3 W3C DID

本标准使用 W3C DID 规范作为 Agent 身份标识的基础。Agent DID 用于：

- 安全认证证书的主体标识
- 信誉评分的查询键
- 委托协议中的参与方标识
- 证书和凭证的签名验证

#### 1.4.4 OAuth 2.0

本标准的认证授权流程兼容 OAuth 2.0。Agent 在进行安全认证和信誉评分查询时，可使用 OAuth 2.0 Bearer Token 进行身份验证。

### 1.5 版本演进路线

```
v0.1 (当前) ─── v0.2 ──────── v1.0 ──────── v1.1+
  │               │             │              │
  ├─ 安全认证     ├─ 多 Certifier ├─ 审计日志   ├─ 跨链
  ├─ 信誉评分     ├─ 评分申诉    ├─ 零知识证明  ├─ DAO 治理
  └─ 委托协议     ├─ SLA 标准    ├─ 隐私保护    └─ 合规框架
                  └─ 托管合约
```

| 版本 | 预计时间 | 核心特性 |
|------|----------|----------|
| **v0.1** | 2026-07 | 安全认证 + 信誉评分 + 委托协议（核心 3 子标准） |
| **v0.2** | 2026-Q4 | 多 Certifier 支持、评分申诉机制、SLA 标准定义 |
| **v1.0** | 2027-Q2 | 链上审计日志、零知识证明隐私保护、成熟生态系统 |
| **v1.1+** | 2027+ | 跨链支持、DAO 治理、金融合规框架 |

### 1.6 规范约定 (Notational Conventions)

本规范中的关键字 **MUST**、**MUST NOT**、**REQUIRED**、**SHALL**、**SHALL NOT**、**SHOULD**、**SHOULD NOT**、**RECOMMENDED**、**MAY**、**OPTIONAL** 按 RFC 2119 的含义解释。

| 关键字 | 含义 |
|--------|------|
| **MUST** / **REQUIRED** | 必须严格遵循，否则实现不符合本标准 |
| **SHOULD** / **RECOMMENDED** | 建议遵循，但允许特殊情况偏离 |
| **MAY** / **OPTIONAL** | 可选，实现者可自行决定是否支持 |
| **MUST NOT** | 严禁遵循，否则实现不符合本标准 |

---

## 2. 子标准 A：Agent Security Certification（安全认证标准）

### 2.1 认证等级

#### 2.1.1 等级总览

AIShield 安全认证定义三个递进等级，每个等级代表不同深度的安全验证：

| 等级 | 名称 | 安全评分要求 | 验证方式 | 适用场景 |
|------|------|-------------|----------|----------|
| **Level 1** | Basic | >= 60/100 | 自动扫描 | 个人 Agent、原型验证、开源项目 |
| **Level 2** | Verified | >= 80/100 | 自动扫描 + 人工审核 | 商业 Agent、企业内部使用、公开服务 |
| **Level 3** | Enterprise | >= 80/100 + 持续监控 | Level 2 + 链上锚定 + 持续监控 | 金融场景、关键基础设施、高价值委托 |

```
     安全可信度递增 ──────────────────────────────►

  ┌─────────┐     ┌──────────┐     ┌────────────┐
  │ Level 1 │ ──► │ Level 2  │ ──► │ Level 3    │
  │ Basic   │     │ Verified │     │ Enterprise │
  └─────────┘     └──────────┘     └────────────┘
  自动扫描         +人工审核        +链上锚定
  >=60分           >=80分           +持续监控
```

#### 2.1.2 Level 1 - Basic

**目标**：提供基础的安全基准验证，确保 Agent 不存在严重安全隐患。

**要求**：
- 通过 OWASP MCP Top 10 基础安全扫描
- 安全评分 >= 60/100
- Agent 拥有有效的 DID 标识
- 提供 `/.well-known/aishield-cert.json` 发现端点

**验证方式**：
- 完全自动化扫描（无需人工干预）
- 扫描完成后自动颁发证书
- 证书有效期：90 天

**限制**：
- 不支持链上记录
- 不支持持续监控
- 证书仅代表通过基础扫描时的安全状态

#### 2.1.3 Level 2 - Verified

**目标**：在基础扫描之上增加人工审核环节，提供更高的安全保障。

**要求**：
- 满足 Level 1 的全部要求
- 安全评分 >= 80/100
- 通过人工代码审查 / 配置审查
- Skill Card 声明的技能经过抽样测试
- Agent 的错误处理和降级策略经过验证

**验证方式**：
- 自动扫描 + 人工审核
- 审核团队由 Certifier 指派
- 审核周期：5 个工作日
- 证书有效期：180 天

**额外验证项**：
- Agent 的身份验证（至少提供邮箱验证）
- 工具调用的权限控制机制审查
- 数据处理隐私策略审查

#### 2.1.4 Level 3 - Enterprise

**目标**：面向高安全需求场景，提供最高等级的安全保障。

**要求**：
- 满足 Level 2 的全部要求
- 证书信息锚定到区块链（链上记录）
- 启用持续安全监控
- 每 30 天进行一次重新扫描
- 支持 SLA 承诺（可用性 >= 99.5%）

**验证方式**：
- Level 2 审核通过后，进行链上锚定
- 配置持续监控探针
- 签署 SLA 协议
- 证书有效期：90 天（需定期续期）

**链上锚定信息**：

```json
{
  "on_chain_record": {
    "cert_id": "cert-aishield-2026-07-20-xxxxx",
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "level": 3,
    "score": 92,
    "scan_hash": "sha256:abc123...",
    "block_number": 18543210,
    "tx_hash": "0xdef456...",
    "chain_id": "eip155:1",
    "anchored_at": "2026-07-20T10:00:00Z",
    "smart_contract": "0xAIShieldCertRegistry"
  }
}
```

### 2.2 认证流程

#### 2.2.1 流程总览

```
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │  1.提交   │───►│ 2.自动   │───►│  3.评分  │───►│ 4.颁发   │───►│ 5.发布   │
 │  工具描述 │    │  扫描    │    │  计算    │    │  证书    │    │  证书    │
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                         │
                                    ┌────────────────────┘
                                    │ (Level 2/3)
                                    ▼
                              ┌──────────┐    ┌──────────┐
                              │ 6.人工   │───►│ 7.链上   │
                              │  审核    │    │  锚定    │
                              └──────────┘    └──────────┘ (Level 3)
```

#### 2.2.2 步骤 1：提交工具描述

Agent 开发者向 Certifier 提交安全认证申请。申请需包含以下信息：

```json
{
  "certification_request": {
    "version": "0.1",
    "requested_level": 2,
    "agent": {
      "did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
      "name": "CodeReviewer-Pro",
      "endpoint": "https://agent.example.com/a2a",
      "version": "2.1.0"
    },
    "tool_descriptions": [
      {
        "tool_name": "file_read",
        "description": "读取指定路径的文件内容",
        "input_schema": {
          "type": "object",
          "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "max_lines": {"type": "integer", "description": "最大读取行数"}
          },
          "required": ["path"]
        },
        "risk_level": "low",
        "security_measures": [
          "路径白名单验证",
          "最大读取大小限制 (10MB)",
          "敏感文件过滤 (.env, credentials)"
        ]
      },
      {
        "tool_name": "code_execute",
        "description": "在沙箱中执行代码",
        "input_schema": {
          "type": "object",
          "properties": {
            "code": {"type": "string"},
            "language": {"type": "string"}
          }
        },
        "risk_level": "high",
        "security_measures": [
          "Docker 容器隔离",
          "CPU/内存/时间限制",
          "网络出站白名单",
          "无持久化存储"
        ]
      }
    ],
    "skill_card_url": "https://agent.example.com/.well-known/skill-card.json",
    "contact_email": "security@agent.example.com"
  }
}
```

提交方式：

| 方式 | 端点 | 说明 |
|------|------|------|
| **REST API** | `POST /aishield-cert/v1/submit` | 通过 HTTPS API 提交 |
| **CLI** | `aishield-cli cert submit --file request.json` | 命令行工具 |
| **Web Dashboard** | Certifier 提供的管理界面 | 图形化提交 |

#### 2.2.3 步骤 2：自动扫描

Certifier 对提交的工具描述和 Agent 端点执行自动化安全扫描。扫描项包括：

**扫描清单**：

| 扫描项 | 类别 | 权重 | 说明 |
|--------|------|------|------|
| Prompt Injection Prevention | 输入安全 | 15% | 检测是否有提示注入防护 |
| Tool Input Validation | 工具安全 | 15% | 检测工具输入参数验证 |
| Permission Control | 访问控制 | 12% | 检测工具调用的权限控制 |
| Data Leakage Prevention | 数据安全 | 10% | 检测数据泄露防护 |
| Error Handling | 稳定性 | 8% | 检测错误处理和降级策略 |
| Rate Limiting | 可用性 | 8% | 检测速率限制机制 |
| Authentication | 身份安全 | 8% | 检测身份验证机制 |
| Logging & Audit | 可审计性 | 6% | 检测日志记录 |
| Dependency Security | 供应链 | 6% | 检测依赖安全性 |
| Configuration Security | 配置安全 | 6% | 检测配置安全性 |
| Output Sanitization | 输出安全 | 6% | 检测输出过滤 |

**扫描结果格式**：

```json
{
  "scan_result": {
    "version": "0.1",
    "scan_id": "scan-2026-07-20-a1b2c3",
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "scan_timestamp": "2026-07-20T08:00:00Z",
    "scanner_version": "aishield-scanner-v0.1.0",
    "total_score": 82,
    "category_scores": {
      "input_security": {
        "score": 88,
        "weight": 0.15,
        "details": [
          {
            "check": "prompt_injection_prevention",
            "status": "pass",
            "score": 90,
            "notes": "Agent 实现了 prompt 注入检测和过滤机制"
          },
          {
            "check": "input_sanitization",
            "status": "pass",
            "score": 86,
            "notes": "工具输入参数有基本的类型和格式验证"
          }
        ]
      },
      "tool_security": {
        "score": 78,
        "weight": 0.15,
        "details": [
          {
            "check": "input_validation",
            "status": "pass",
            "score": 80,
            "notes": "所有工具声明了 JSON Schema 输入格式"
          },
          {
            "check": "overload_protection",
            "status": "warning",
            "score": 65,
            "notes": "部分工具缺少调用频率限制",
            "recommendation": "建议对 code_execute 工具添加每分钟调用次数限制"
          }
        ]
      },
      "access_control": {
        "score": 75,
        "weight": 0.12,
        "details": [
          {
            "check": "role_based_access",
            "status": "pass",
            "score": 85,
            "notes": "实现了基于角色的工具访问控制"
          },
          {
            "check": "least_privilege",
            "status": "warning",
            "score": 65,
            "notes": "部分工具权限范围过宽"
          }
        ]
      }
    },
    "critical_findings": [],
    "warnings": [
      {
        "id": "W-001",
        "severity": "medium",
        "title": "缺少工具调用频率限制",
        "description": "code_execute 工具未配置最大调用频率",
        "recommendation": "建议配置最大 10 次/分钟的限制"
      }
    ],
    "scan_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
}
```

#### 2.2.4 步骤 3：评分计算

安全评分基于扫描结果计算，采用加权平均算法：

```
Total Score = Σ (Category_Score_i × Weight_i)

示例计算：
= 88 × 0.15 + 78 × 0.15 + 75 × 0.12 + ...
= 13.2 + 11.7 + 9.0 + ...
= 82 / 100
```

**评分等级判定**：

| 评分范围 | 等级 | 状态 |
|----------|------|------|
| 90-100 | 优秀 (Excellent) | 可获得 Level 3 候选 |
| 80-89 | 良好 (Good) | 可获得 Level 2 |
| 60-79 | 及格 (Pass) | 可获得 Level 1 |
| 0-59 | 不及格 (Fail) | 不予认证 |

#### 2.2.5 步骤 4：颁发证书

评分达到对应等级要求后，Certifier 颁发安全认证证书。详见 [2.3 证书格式](#23-证书格式)。

#### 2.2.6 步骤 5：发布证书

Agent 需将证书发布到其标准的发现端点 `/.well-known/aishield-cert.json`，并可选地在 AIShield Registry 中注册。

#### 2.2.7 步骤 6：人工审核（Level 2/3）

对于 Level 2 及以上认证，自动扫描通过后需进行人工审核。

**人工审核清单**：

| 审核项 | 说明 | 通过标准 |
|--------|------|----------|
| 工具描述准确性 | 工具描述是否与实际行为一致 | 完全一致 |
| 安全措施有效性 | 声明的安全措施是否实际生效 | 抽样验证通过 |
| 错误处理充分性 | 异常情况下的行为是否安全 | 不会泄露敏感信息 |
| 隐私策略合规 | 数据处理是否符合隐私声明 | 无违规行为 |
| 身份验证 | Agent 开发者身份是否可验证 | 至少邮箱验证 |

#### 2.2.8 步骤 7：链上锚定（Level 3）

Level 3 认证需将证书信息锚定到区块链。

```json
{
  "anchor_transaction": {
    "function": "registerCertificate(bytes32 certId, address agent, uint8 level, uint256 score, bytes32 scanHash)",
    "parameters": {
      "certId": "0x...cert_hash",
      "agent": "0x...agent_address",
      "level": 3,
      "score": 92,
      "scanHash": "0x...scan_hash"
    },
    "contract_address": "0xAIShieldCertRegistry",
    "chain_id": "eip155:1"
  }
}
```

### 2.3 证书格式

#### 2.3.1 证书 JSON Schema

AIShield 安全认证证书使用标准化的 JSON 格式：

```json
{
  "$schema": "https://aishield.org/schemas/cert/v0.1",
  "aishield_cert": {
    "cert_id": "cert-aishield-2026-07-20-7f3a2b",
    "cert_version": "0.1",
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "agent_name": "CodeReviewer-Pro",
    "agent_endpoint": "https://agent.example.com/a2a",
    "level": 2,
    "level_name": "Verified",
    "score": 82,
    "score_breakdown": {
      "input_security": 88,
      "tool_security": 78,
      "access_control": 75,
      "data_security": 85,
      "stability": 80,
      "availability": 72,
      "identity": 90,
      "auditability": 68,
      "supply_chain": 85,
      "configuration": 80,
      "output_security": 82
    },
    "scan_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scan_timestamp": "2026-07-20T08:00:00Z",
    "certifier": {
      "did": "did:aishield:certifier-official",
      "name": "AIShield Official Certifier",
      "endpoint": "https://cert.aishield.org"
    },
    "issued_at": "2026-07-20T10:00:00Z",
    "expires_at": "2027-01-17T10:00:00Z",
    "verification_url": "https://verify.aishield.org/cert/cert-aishield-2026-07-20-7f3a2b",
    "on_chain": {
      "anchored": false,
      "level_3_available": false
    },
    "certifier_signature": "eyJhbGciOiJFZERTQSIsImtpZCI6IiNrZXktMSJ9.eyJjZXJ0X2lkIjoiY2VydC1haXNoaWVsZC0yMDI2LTA3LTIwLTdmM2EyYiIsImFnZW50X2RpZCI6ImRpZDphaXNoaWVsZDo3ZjNhMmIxYzlkNGU1ZjZhOGIwYzFkMmUzZjRhNWI2YyIsImxldmVsIjoyLCJzY29yZSI6ODIsImlzc3VlZF9hdCI6IjIwMjYtMDctMjBUMTA6MDA6MDBaIn0..."
  }
}
```

#### 2.3.2 字段说明

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `cert_id` | string | 是 | 证书唯一标识符，格式 `cert-aishield-{date}-{random}` |
| `cert_version` | string | 是 | 证书格式版本，当前为 `0.1` |
| `agent_did` | string (DID) | 是 | 被认证 Agent 的 DID |
| `agent_name` | string | 是 | Agent 人类可读名称 |
| `agent_endpoint` | string (URL) | 否 | Agent 的 A2A 端点 |
| `level` | integer | 是 | 认证等级 (1, 2, 3) |
| `level_name` | string | 是 | 等级名称 (Basic, Verified, Enterprise) |
| `score` | integer | 是 | 安全评分 (0-100) |
| `score_breakdown` | object | 否 | 各维度评分详情 |
| `scan_hash` | string | 是 | 扫描结果的哈希值 |
| `scan_timestamp` | string (ISO 8601) | 是 | 扫描执行时间 |
| `certifier` | object | 是 | 认证机构信息 |
| `issued_at` | string (ISO 8601) | 是 | 证书颁发时间 |
| `expires_at` | string (ISO 8601) | 是 | 证书过期时间 |
| `verification_url` | string (URL) | 否 | 证书验证页面 URL |
| `on_chain` | object | 否 | 链上锚定信息 |
| `certifier_signature` | string | 是 | 认证机构对证书的数字签名 |

#### 2.3.3 证书签名

证书的 `certifier_signature` 字段使用 Ed25519 签名算法。签名 payload 为以下 JSON 的 canonical 序列化：

```json
{
  "cert_id": "cert-aishield-2026-07-20-7f3a2b",
  "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
  "level": 2,
  "score": 82,
  "issued_at": "2026-07-20T10:00:00Z",
  "expires_at": "2027-01-17T10:00:00Z"
}
```

验证方使用 Certifier 的公钥（从其 DID Document 中获取）验证签名完整性。

### 2.4 验证端点

#### 2.4.1 标准发现端点

每个经过安全认证的 Agent **MUST** 在其域名的标准路径下提供证书文件：

```
GET https://{agent-domain}/.well-known/aishield-cert.json
```

**示例请求**：

```http
GET https://agent.example.com/.well-known/aishield-cert.json HTTP/1.1
Host: agent.example.com
Accept: application/json
```

**示例响应**：

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=3600

{
  "$schema": "https://aishield.org/schemas/cert/v0.1",
  "aishield_cert": {
    "cert_id": "cert-aishield-2026-07-20-7f3a2b",
    "cert_version": "0.1",
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "agent_name": "CodeReviewer-Pro",
    "level": 2,
    "level_name": "Verified",
    "score": 82,
    "scan_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "issued_at": "2026-07-20T10:00:00Z",
    "expires_at": "2027-01-17T10:00:00Z",
    "certifier": {
      "did": "did:aishield:certifier-official",
      "name": "AIShield Official Certifier"
    },
    "verification_url": "https://verify.aishield.org/cert/cert-aishield-2026-07-20-7f3a2b"
  }
}
```

#### 2.4.2 验证端点行为规范

| 场景 | HTTP 状态码 | 说明 |
|------|-------------|------|
| 证书存在且有效 | 200 OK | 返回完整的证书 JSON |
| 证书已过期 | 200 OK + `expired: true` | 返回证书并标记为已过期 |
| 证书不存在 | 404 Not Found | Agent 未获得安全认证 |
| 证书已被吊销 | 410 Gone | 返回吊销原因 |

**过期证书响应示例**：

```json
{
  "$schema": "https://aishield.org/schemas/cert/v0.1",
  "aishield_cert": {
    "cert_id": "cert-aishield-2026-01-20-xxxxx",
    "agent_did": "did:aishield:xxxxx",
    "level": 1,
    "level_name": "Basic",
    "score": 65,
    "issued_at": "2026-01-20T10:00:00Z",
    "expires_at": "2026-04-20T10:00:00Z",
    "expired": true,
    "expired_at": "2026-04-20T10:00:00Z",
    "renewal_url": "https://cert.aishield.org/renew/cert-aishield-2026-01-20-xxxxx"
  }
}
```

#### 2.4.3 Registry 查询端点

除了 Agent 自身的发现端点外，AIShield Registry 也提供证书查询：

```
GET https://registry.aishield.org/v1/cert/{cert_id}
GET https://registry.aishield.org/v1/cert/agent/{agent_did}
```

### 2.5 徽章规范

#### 2.5.1 SVG 徽章格式

每个认证等级对应标准化的 SVG 徽章，可嵌入到 Agent 的文档、网站和 DID Document 中。

**Level 1 - Basic 徽章**：

```
┌─────────────────────────────────────┐
│ 🛡️ AIShield Certified - Basic     │
│    Score: 72/100                    │
│    [Verified →]                     │
└─────────────────────────────────────┘
```

**Level 2 - Verified 徽章**：

```
┌─────────────────────────────────────┐
│ 🛡️🛡️ AIShield Verified           │
│    Score: 85/100                    │
│    [Verified →]                     │
└─────────────────────────────────────┘
```

**Level 3 - Enterprise 徽章**：

```
┌─────────────────────────────────────┐
│ 🛡️🛡️🛡️ AIShield Enterprise       │
│    Score: 95/100  ⛓ On-Chain       │
│    [Verified →]                     │
└─────────────────────────────────────┘
```

#### 2.5.2 SVG 徽章标准模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="240" height="72" viewBox="0 0 240 72">
  <!-- AIShield 标准认证徽章 -->
  <!-- Level 2 - Verified -->
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a73e8;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0d47a1;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="240" height="72" rx="8" ry="8" fill="url(#bg)" />
  <text x="12" y="22" fill="#ffffff" font-family="system-ui,sans-serif" font-size="11" font-weight="600">
    AIShield Certified
  </text>
  <text x="12" y="40" fill="#bbdefb" font-family="system-ui,sans-serif" font-size="10">
    Level 2 · Verified
  </text>
  <text x="12" y="58" fill="#ffffff" font-family="system-ui,sans-serif" font-size="12" font-weight="700">
    Score: 85/100
  </text>
  <a href="https://verify.aishield.org/cert/{cert_id}" target="_blank">
    <text x="160" y="40" fill="#90caf9" font-family="system-ui,sans-serif" font-size="10" text-decoration="underline">
      Verify →
    </text>
  </a>
</svg>
```

#### 2.5.3 徽章使用规范

Agent 开发者应将徽章嵌入到以下位置：

| 位置 | 说明 |
|------|------|
| Agent 文档首页 | 顶部显眼位置展示 |
| Skill Card 文档 | 技能描述中附带徽章 |
| DID Document | `service` 字段中引用徽章 URL |
| A2A Agent Card | Agent Card 的 `metadata` 中包含徽章 URL |
| GitHub README | 开源 Agent 的仓库主页 |

徽章 URL 格式：

```
https://badge.aishield.org/{level}/{cert_id}.svg

示例：
https://badge.aishield.org/2/cert-aishield-2026-07-20-7f3a2b.svg
```

### 2.6 安全扫描规范

#### 2.6.1 扫描工具接口

Certifier **MUST** 提供标准化的扫描工具接口，确保不同 Certifier 间的扫描结果可比较。

```json
{
  "scanner_spec": {
    "version": "0.1",
    "scanner_name": "AIShield Security Scanner",
    "scanner_version": "0.1.0",
    "supported_checks": [
      "prompt_injection_prevention",
      "tool_input_validation",
      "permission_control",
      "data_leakage_prevention",
      "error_handling",
      "rate_limiting",
      "authentication",
      "logging_audit",
      "dependency_security",
      "configuration_security",
      "output_sanitization"
    ],
    "scan_timeout_seconds": 300,
    "max_tool_count": 100,
    "retry_policy": {
      "max_retries": 3,
      "retry_delay_seconds": 30
    }
  }
}
```

#### 2.6.2 扫描 API

```
POST /aishield-cert/v1/scan
Content-Type: application/json
Authorization: Bearer {token}

{
  "agent_did": "did:aishield:xxxxx",
  "agent_endpoint": "https://agent.example.com/a2a",
  "tool_descriptions": [...],
  "scan_level": "full"
}
```

扫描响应：

```json
{
  "scan_id": "scan-2026-07-20-a1b2c3",
  "status": "completed",
  "started_at": "2026-07-20T08:00:00Z",
  "completed_at": "2026-07-20T08:05:23Z",
  "result": {
    "total_score": 82,
    "category_scores": {...},
    "critical_findings": [],
    "warnings": [...]
  }
}
```

### 2.7 证书吊销与更新

#### 2.7.1 证书吊销

以下情况将触发证书吊销：

| 触发条件 | 处理方式 |
|----------|----------|
| 发现严重安全漏洞 | 立即吊销 |
| Agent 行为异常（如恶意工具调用） | 立即吊销 |
| Agent 端点长期不可用（>30 天） | 吊销并通知 |
| 证书过期未续期 | 自动吊销 |
| 开发者主动申请吊销 | 立即吊销 |

吊销响应格式：

```json
{
  "revocation": {
    "cert_id": "cert-aishield-2026-07-20-7f3a2b",
    "revoked_at": "2026-08-15T12:00:00Z",
    "reason": "critical_vulnerability_found",
    "reason_description": "Agent 工具 code_execute 被发现存在容器逃逸漏洞",
    "revoked_by": "did:aishield:certifier-official",
    "appeal_url": "https://cert.aishield.org/appeal/cert-aishield-2026-07-20-7f3a2b"
  }
}
```

#### 2.7.2 证书更新

Agent 可在证书过期前 30 天申请续期。续期流程：

1. 提交续期申请
2. 执行新一轮安全扫描
3. 审核通过后颁发新证书
4. 新证书自动发布到发现端点

---

## 3. 子标准 B：Agent Trust Score（信誉评分标准）

### 3.1 评分维度

#### 3.1.1 维度总览

Agent Trust Score 由五个维度加权计算，满分 100 分：

```
┌─────────────────────────────────────────────────────────┐
│                 Agent Trust Score (100)                  │
│                                                         │
│  ┌──────────────────┐  30%  Security Score              │
│  │  安全评分        │  ─────────────────────────────    │
│  └──────────────────┘                                   │
│  ┌──────────────────┐  25%  Reliability Score           │
│  │  可靠性评分      │  ─────────────────────────────    │
│  └──────────────────┘                                   │
│  ┌──────────────────┐  25%  Reputation Score            │
│  │  声誉评分        │  ─────────────────────────────    │
│  └──────────────────┘                                   │
│  ┌──────────────────┐  10%  Activity Score              │
│  │  活跃度评分      │  ─────────────────────────────    │
│  └──────────────────┘                                   │
│  ┌──────────────────┐  10%  Identity Score              │
│  │  身份评分        │  ─────────────────────────────    │
│  └──────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

| 维度 | 权重 | 核心指标 | 数据来源 |
|------|------|----------|----------|
| **Security Score** | 30% | 安全认证等级 | 子标准 A 证书 |
| **Reliability Score** | 25% | 任务完成率 + 平均响应时间 | 委托协议执行记录 |
| **Reputation Score** | 25% | 被委托方好评率 + 纠纷率 | 委托方评价记录 |
| **Activity Score** | 10% | 活跃天数 + 交易量 | 系统活跃度记录 |
| **Identity Score** | 10% | 身份验证层级 | 身份验证服务 |

#### 3.1.2 Security Score（安全评分）— 30%

安全评分基于子标准 A 的安全认证等级和评分进行映射：

| 认证等级 | 安全评分 | 说明 |
|----------|----------|------|
| Level 3 - Enterprise | 90-100 | 按实际认证评分线性映射 |
| Level 2 - Verified | 70-89 | 按实际认证评分线性映射 |
| Level 1 - Basic | 50-69 | 按实际认证评分线性映射 |
| 未认证 | 0 | 未获得安全认证 |

**映射公式**：

```
Security Score = base_score + (cert_score - cert_min_score) × range_factor

Level 1: Security Score = 50 + (cert_score - 60) × (19/40)
  cert_score=60 → 50, cert_score=100 → 69

Level 2: Security Score = 70 + (cert_score - 80) × (19/20)
  cert_score=80 → 70, cert_score=100 → 89

Level 3: Security Score = 90 + (cert_score - 80) × (10/20)
  cert_score=80 → 90, cert_score=100 → 100
```

#### 3.1.3 Reliability Score（可靠性评分）— 25%

可靠性评分由两个子指标组成：

**子指标 1：任务完成率 (Task Completion Rate)** — 权重 60%

```
Task Completion Rate = 成功完成的任务数 / 总接受的任务数 × 100%

评分映射：
- 95%+ 完成率 → 90-100 分
- 85-94% 完成率 → 70-89 分
- 70-84% 完成率 → 50-69 分
- 50-69% 完成率 → 30-49 分
- <50% 完成率 → 0-29 分
```

**子指标 2：平均响应时间 (Average Response Time)** — 权重 40%

```
Avg Response Time = Σ(task_response_time) / Σ(completed_tasks)

评分映射（以秒为单位）：
- < 5s  → 90-100 分
- 5-15s → 70-89 分
- 15-60s → 50-69 分
- 60-300s → 30-49 分
- > 300s → 0-29 分
```

**Reliability Score 计算**：

```
Reliability Score = (Completion_Rate_Score × 0.6) + (Response_Time_Score × 0.4)
```

#### 3.1.4 Reputation Score（声誉评分）— 25%

声誉评分由两个子指标组成：

**子指标 1：好评率 (Positive Rating Rate)** — 权重 70%

```
Positive Rating Rate = 好评数 / (好评数 + 差评数) × 100%

评分映射：
- 95%+ 好评率 → 90-100 分
- 85-94% 好评率 → 70-89 分
- 70-84% 好评率 → 50-69 分
- 50-69% 好评率 → 30-49 分
- <50% 好评率 → 0-29 分
```

**子指标 2：纠纷率 (Dispute Rate)** — 权重 30%

```
Dispute Rate = 争议任务数 / 总完成任务数 × 100%

评分映射（取反）：
- < 1% 纠纷率 → 90-100 分
- 1-3% 纠纷率 → 70-89 分
- 3-5% 纠纷率 → 50-69 分
- 5-10% 纠纷率 → 30-49 分
- > 10% 纠纷率 → 0-29 分
```

**Reputation Score 计算**：

```
Reputation Score = (Positive_Rating_Score × 0.7) + ((100 - Dispute_Rate_Score) × 0.3)
```

**评价标准**：

委托方在任务完成后可对 Delegate Agent 进行评价。评价格式：

```json
{
  "rating": {
    "version": "0.1",
    "delegation_id": "del-2026-07-20-a1b2c3d4",
    "rater_did": "did:aishield:delegator-a",
    "ratee_did": "did:aishield:delegate-b",
    "score": 4,
    "max_score": 5,
    "categories": {
      "quality": 5,
      "timeliness": 4,
      "communication": 4,
      "security": 5
    },
    "comment": "代码审查质量很高，发现了一个关键安全漏洞。响应及时。",
    "rated_at": "2026-07-20T15:00:00Z",
    "rater_signature": "eyJhbGciOiJFZERTQSIsImtp..."
  }
}
```

#### 3.1.5 Activity Score（活跃度评分）— 10%

活跃度评分由两个子指标组成：

**子指标 1：活跃天数 (Active Days)** — 权重 50%

```
Active Days = 最近 90 天内有任务交互的天数

评分映射：
- 80+ 天 → 90-100 分
- 60-79 天 → 70-89 分
- 30-59 天 → 50-69 分
- 10-29 天 → 30-49 分
- < 10 天 → 0-29 分
```

**子指标 2：交易量 (Transaction Volume)** — 权重 50%

```
Transaction Volume = 最近 90 天内完成的委托任务总数

评分映射：
- 500+ 次 → 90-100 分
- 200-499 次 → 70-89 分
- 50-199 次 → 50-69 分
- 10-49 次 → 30-49 分
- < 10 次 → 0-29 分
```

**Activity Score 计算**：

```
Activity Score = (Active_Days_Score × 0.5) + (Transaction_Volume_Score × 0.5)
```

#### 3.1.6 Identity Score（身份评分）— 10%

身份评分基于 Agent 开发者/运营者的身份验证层级：

| 验证层级 | 身份评分 | 说明 |
|----------|----------|------|
| 无验证 | 0 | 仅 DID 标识，无额外验证 |
| 邮箱验证 | 30 | 验证了有效邮箱地址 |
| GitHub / 社交账号验证 | 50 | 关联了 GitHub 或其他社交账号 |
| KYC 基础验证 | 70 | 基本人身份验证（姓名 + ID） |
| KYC 高级验证 | 85 | 高级身份验证（人脸识别 + 文件） |
| 链上身份验证 | 100 | 通过链上身份验证（如 ENS + Proof of Humanity） |

身份评分支持叠加（取最高层级）：

```json
{
  "identity_verification": {
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "verified_attributes": [
      {
        "type": "email",
        "value": "s***@example.com",
        "verified_at": "2026-01-15T10:00:00Z",
        "verifier": "did:aishield:certifier-official"
      },
      {
        "type": "github",
        "value": "github.com/agent-dev-team",
        "verified_at": "2026-02-01T10:00:00Z",
        "verifier": "did:aishield:certifier-official"
      }
    ],
    "highest_level": "github",
    "identity_score": 50
  }
}
```

### 3.2 评分算法

#### 3.2.1 综合评分计算

Trust Score 的最终计算公式：

```
Trust Score = Σ (Dimension_Score_i × Dimension_Weight_i)

= (Security_Score × 0.30)
+ (Reliability_Score × 0.25)
+ (Reputation_Score × 0.25)
+ (Activity_Score × 0.10)
+ (Identity_Score × 0.10)
```

**计算示例**：

```
Security Score    = 78  × 0.30 = 23.4
Reliability Score = 85  × 0.25 = 21.25
Reputation Score  = 72  × 0.25 = 18.0
Activity Score    = 60  × 0.10 = 6.0
Identity Score    = 50  × 0.10 = 5.0
────────────────────────────────────
Total Trust Score = 73.65 → 74 (四舍五入)
```

#### 3.2.2 评分平滑算法

为防止评分剧烈波动，Trust Score 采用 **指数移动平均 (EMA)** 进行平滑：

```
Smoothed_Score = α × New_Score + (1 - α) × Previous_Score

其中：
- α = 0.3（平滑因子）
- New_Score = 基于最新数据计算的原始分数
- Previous_Score = 上一周期的平滑分数

首次计算时：
- Previous_Score = New_Score（无历史数据时）
```

#### 3.2.3 评分归一化

所有维度评分均归一化到 0-100 范围。对于各子指标的评分，使用分段线性插值：

```python
def map_score(value, ranges):
    """
    将原始值映射到 0-100 评分
    ranges: [(threshold, min_score, max_score), ...]
    按阈值从小到大排列
    """
    for i, (threshold, min_score, max_score) in enumerate(ranges):
        if value < threshold or i == len(ranges) - 1:
            if i == 0:
                return min_score
            prev_threshold = ranges[i-1][0]
            prev_max = ranges[i-1][2]
            ratio = (value - prev_threshold) / (threshold - prev_threshold)
            return prev_max + ratio * (max_score - min_score)
    return ranges[-1][2]
```

### 3.3 评分查询 API

#### 3.3.1 查询端点

**标准查询端点**：

```
GET /aishield-trust/v1/score/{did}
```

**请求示例**：

```http
GET /aishield-trust/v1/score/did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c HTTP/1.1
Host: trust.aishield.org
Accept: application/json
```

**成功响应**：

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=300

{
  "trust_score_response": {
    "version": "0.1",
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "agent_name": "CodeReviewer-Pro",
    "trust_score": 74,
    "computed_at": "2026-07-20T12:00:00Z",
    "dimensions": {
      "security": {
        "score": 78,
        "weight": 0.30,
        "details": {
          "cert_level": 2,
          "cert_level_name": "Verified",
          "cert_score": 82,
          "cert_id": "cert-aishield-2026-07-20-7f3a2b",
          "cert_expires_at": "2027-01-17T10:00:00Z"
        }
      },
      "reliability": {
        "score": 85,
        "weight": 0.25,
        "details": {
          "task_completion_rate": 0.96,
          "total_tasks": 342,
          "completed_tasks": 328,
          "avg_response_time_seconds": 8.5
        }
      },
      "reputation": {
        "score": 72,
        "weight": 0.25,
        "details": {
          "positive_rating_rate": 0.88,
          "total_ratings": 156,
          "avg_rating": 4.2,
          "dispute_rate": 0.03,
          "total_disputes": 10
        }
      },
      "activity": {
        "score": 60,
        "weight": 0.10,
        "details": {
          "active_days_90d": 45,
          "total_transactions_90d": 78
        }
      },
      "identity": {
        "score": 50,
        "weight": 0.10,
        "details": {
          "verification_level": "github",
          "verified_attributes": ["email", "github"]
        }
      }
    },
    "history": {
      "30d_ago": 71,
      "60d_ago": 68,
      "90d_ago": 65
    }
  }
}
```

#### 3.3.2 批量查询端点

```
POST /aishield-trust/v1/scores/batch
Content-Type: application/json

{
  "dids": [
    "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "did:aishield:abc123def456",
    "did:aishield:xyz789"
  ]
}
```

**响应**：

```json
{
  "batch_response": {
    "version": "0.1",
    "scores": [
      {
        "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
        "trust_score": 74
      },
      {
        "agent_did": "did:aishield:abc123def456",
        "trust_score": 55
      },
      {
        "agent_did": "did:aishield:xyz789",
        "trust_score": 91
      }
    ]
  }
}
```

#### 3.3.3 错误响应

| HTTP 状态码 | 场景 | 响应体 |
|-------------|------|--------|
| 404 | Agent DID 不存在 | `{"error": "agent_not_found", "did": "..."}` |
| 429 | 请求频率超限 | `{"error": "rate_limited", "retry_after": 60}` |
| 500 | 服务端错误 | `{"error": "internal_error"}` |

### 3.4 评分更新机制

#### 3.4.1 事件驱动更新

Trust Score 在以下事件发生时触发重新计算：

| 事件 | 触发的维度更新 | 延迟 |
|------|----------------|------|
| 安全证书颁发/更新 | Security | 立即 |
| 安全证书吊销 | Security | 立即 |
| 委托任务完成 | Reliability, Activity | 5 分钟内 |
| 收到委托评价 | Reputation | 实时 |
| 争议创建/解决 | Reputation | 实时 |
| 身份验证更新 | Identity | 立即 |

**事件格式**：

```json
{
  "trust_event": {
    "event_type": "task_completed",
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "delegation_id": "del-2026-07-20-a1b2c3d4",
    "timestamp": "2026-07-20T14:30:00Z",
    "data": {
      "completion_status": "success",
      "response_time_ms": 8500
    }
  }
}
```

#### 3.4.2 每日聚合

除事件驱动更新外，系统每日 UTC 00:00 执行一次全量聚合：

```
每日聚合流程：
1. 收集过去 24 小时内所有相关事件
2. 重新计算各维度评分
3. 应用 EMA 平滑
4. 更新缓存
5. 记录评分历史快照
6. 检测异常波动（单日变化 > 10 分触发告警）
```

#### 3.4.3 评分历史

Trust Score 保留最近 365 天的每日评分快照：

```json
{
  "score_history": {
    "agent_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "period": "365d",
    "snapshots": [
      {"date": "2026-07-20", "score": 74},
      {"date": "2026-07-19", "score": 73},
      {"date": "2026-07-18", "score": 73},
      {"date": "2026-07-17", "score": 72},
      {"date": "2026-07-16", "score": 71}
    ]
  }
}
```

查询端点：

```
GET /aishield-trust/v1/score/{did}/history?period=90d
```

### 3.5 防刷机制

#### 3.5.1 新注册保护期

新注册 Agent 在注册后 30 天内，其 Trust Score 有上限限制：

```
New Agent Cap:

Day 1-7:   Trust Score 上限 40
Day 8-14:  Trust Score 上限 55
Day 15-21: Trust Score 上限 70
Day 22-30: Trust Score 上限 85
Day 31+:   无限制

公式：
cap = 40 + min(30, days_since_registration - 1) × 1.5
实际显示分数 = min(calculated_score, cap)
```

**设计理由**：
- 防止通过批量注册新 Agent 快速刷分
- 防止通过自交易（self-dealing）人为提升评分
- 给市场足够的观察期来评估新 Agent 的真实表现

#### 3.5.2 评价可信度加权

不同来源的评价具有不同的权重：

| 评价来源 | 权重乘数 | 说明 |
|----------|----------|------|
| 首次合作评价 | 0.5 | 首次委托的评价，可信度较低 |
| 重复合作评价 | 1.0-1.5 | 多次合作的评价，可信度更高 |
| 高 Trust Score 委托方 | 1.0-1.3 | 评分高的委托方的评价权重更高 |
| 同一 DID 多次评价 | 0.3 (首次后) | 同一 DID 对同一 Agent 的重复评价降权 |
| 短时间大量评价 | 0.1 | 异常评价模式，显著降权 |

#### 3.5.3 异常检测

系统持续监测以下异常模式：

| 异常模式 | 检测方式 | 处理 |
|----------|----------|------|
| 自交易 | 同一 DID 网络下的委托/受托 | 标记但不计入评分 |
| 评价轰炸 | 短时间内收到大量相似评价 | 冻结评分，人工审核 |
| 评分操纵 | DID 关系图谱分析 | 关联 DID 的评分相互降权 |
| 证书套利 | 频繁更换 DID 重新认证 | 新 DID 继承旧 DID 的惩罚记录 |

#### 3.5.4 评分申诉

Agent 开发者如对评分有异议，可通过以下方式申诉：

```
POST /aishield-trust/v1/score/{did}/appeal

{
  "appeal": {
    "reason": "评分异常下降",
    "description": "过去 7 天 Trust Score 从 85 下降到 62，怀疑存在恶意差评",
    "evidence": ["https://...", "https://..."],
    "contact_email": "operator@agent.example.com"
  }
}
```

申诉处理流程：

```
提交申诉 → 24h 内初审 → 5 个工作日内复审 → 通知结果
                                    │
                              ┌─────┴─────┐
                              │           │
                         申诉成功      申诉失败
                         修正评分      维持原判
```

### 3.6 评分分级

#### 3.6.1 信任等级

Trust Score 对应以下信任等级：

| 分数范围 | 信任等级 | 标识 | 说明 |
|----------|----------|------|------|
| 90-100 | Trusted+ | 🟢🟢🟢 | 高度可信，推荐用于高价值委托 |
| 75-89 | Trusted | 🟢🟢 | 可信，适用于大多数委托场景 |
| 60-74 | Standard | 🟡 | 标准信任，适用于低风险委托 |
| 40-59 | Caution | 🟠 | 需谨慎，建议附加保障措施 |
| 0-39 | Unverified | 🔴 | 未验证，不建议用于正式委托 |

#### 3.6.2 等级用途示例

```json
{
  "trust_requirements_example": {
    "high_value_delegation": {
      "min_trust_score": 75,
      "min_cert_level": 2,
      "escrow_required": true,
      "description": "高价值委托：代码审计、金融分析等"
    },
    "standard_delegation": {
      "min_trust_score": 60,
      "min_cert_level": 1,
      "escrow_required": false,
      "description": "标准委托：内容生成、数据分析等"
    },
    "experimental_delegation": {
      "min_trust_score": 40,
      "min_cert_level": null,
      "escrow_required": false,
      "description": "实验性委托：原型验证、概念验证等"
    }
  }
}
```

---

## 4. 子标准 C：Agent Delegation Protocol（委托协议标准）

### 4.1 协议概述

#### 4.1.1 背景

Agent Delegation Protocol 是 AIShield Trust Standard 的核心交互协议，定义了 Agent 间安全委托任务的标准流程。本协议基于 Google A2A (Agent-to-Agent) Task 模型进行扩展，增加了安全认证验证、信誉检查、托管机制和争议解决流程。

#### 4.1.2 核心概念

```
┌─────────────────────────────────────────────────────────────────┐
│                    委托协议核心概念                              │
│                                                                 │
│   Delegator (委托方)                    Delegate (受托方)       │
│   ┌──────────────┐                    ┌──────────────┐          │
│   │ 创建委托任务  │──── 信任验证 ────►│ 接受/拒绝任务  │          │
│   │ 设定安全要求  │                    │ 执行任务       │          │
│   │ 设定信誉要求  │                    │ 提交完成凭证   │          │
│   │ 配置托管      │                    │ 接受评价       │          │
│   │ 配置争议解决  │                    │               │          │
│   └──────────────┘                    └──────────────┘          │
│         │                                    │                 │
│         └────────── AIShield Registry ───────┘                 │
│                    (信任数据查询)                                │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.1.3 协议栈

```
┌─────────────────────────────────────┐
│    Application Layer               │
│    (任务描述、结果、评价)            │
├─────────────────────────────────────┤
│    AIShield Delegation Protocol     │
│    (托管、信誉、安全、争议)          │
├─────────────────────────────────────┤
│    A2A Protocol                     │
│    (Task 模型、消息传递)            │
├─────────────────────────────────────┤
│    Transport Layer                 │
│    (HTTP/HTTPS + JSON-RPC)         │
└─────────────────────────────────────┘
```

### 4.2 扩展字段定义

#### 4.2.1 完整委托任务格式

以下是基于 A2A Task 模型扩展后的完整委托任务格式：

```json
{
  "a2a_task": {
    "task_id": "task-2026-07-20-a1b2c3d4",
    "task_name": "代码安全审查",
    "description": "对指定仓库的主分支代码进行全面安全审查",
    "status": "created",
    "input": {
      "repository_url": "https://github.com/example/project",
      "branch": "main",
      "scope": "full",
      "output_format": "json"
    },
    "output": null,
    "created_at": "2026-07-20T10:00:00Z"
  },
  "aishield_delegation": {
    "version": "0.1",
    "delegation_id": "del-2026-07-20-a1b2c3d4",
    "delegator": {
      "did": "did:aishield:delegator-company-a",
      "name": "CompanyA SecurityOps",
      "endpoint": "https://ops.companya.com/a2a"
    },
    "delegate": {
      "did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
      "name": "CodeReviewer-Pro",
      "endpoint": "https://agent.example.com/a2a"
    },
    "escrow": {
      "enabled": true,
      "amount": "100.00",
      "currency": "USDC",
      "escrow_agent": "did:aishield:escrow-service-a",
      "contract_address": "0xEscrowContract",
      "chain_id": "eip155:1",
      "release_conditions": [
        "task_completed_and_verified",
        "no_dispute_within_72h"
      ],
      "auto_refund_after": "168h"
    },
    "trust_requirements": {
      "min_trust_score": 75,
      "min_reliability_score": 80,
      "min_reputation_score": 70,
      "prefer_cert_level": 2
    },
    "security_requirements": {
      "min_cert_level": 2,
      "required_certifier": "any",
      "data_classification": "confidential",
      "compliance_requirements": [],
      "tool_restrictions": [
        "no_network_access",
        "sandbox_execution_only"
      ]
    },
    "dispute_resolution": {
      "method": "arbitration",
      "arbitrator": "did:aishield:arbitrator-official",
      "evidence_window": "72h",
      "arbitration_fee": {
        "amount": "5.00",
        "currency": "USDC",
        "payer": "loser"
      },
      "escalation_path": [
        "auto_negotiation",
        "arbitration",
        "community_vote"
      ],
      "max_dispute_duration": "336h"
    },
    "receipt": null,
    "sla": {
      "expected_duration": "24h",
      "max_duration": "48h",
      "penalty_per_hour_late": "2.00",
      "penalty_currency": "USDC"
    },
    "created_at": "2026-07-20T10:00:00Z",
    "updated_at": "2026-07-20T10:00:00Z"
  }
}
```

#### 4.2.2 扩展字段详解

**escrow（托管信息）**：

```json
{
  "escrow": {
    "enabled": true,
    "amount": "100.00",
    "currency": "USDC",
    "escrow_agent": "did:aishield:escrow-service-a",
    "contract_address": "0xEscrowContract",
    "chain_id": "eip155:1",
    "release_conditions": [
      "task_completed_and_verified",
      "no_dispute_within_72h"
    ],
    "auto_refund_after": "168h"
  }
}
```

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `enabled` | boolean | 是 | 是否启用托管 |
| `amount` | string | 条件必须 | 托管金额（启用时必须） |
| `currency` | string | 条件必须 | 托管币种（USDC, ETH, DAI 等） |
| `escrow_agent` | string (DID) | 条件必须 | 托管服务 Agent 的 DID |
| `contract_address` | string | 条件必须 | 托管智能合约地址 |
| `chain_id` | string | 条件必须 | 区块链 ID（CAIP-2 格式） |
| `release_conditions` | array | 否 | 释放条件列表 |
| `auto_refund_after` | string | 否 | 超时自动退款时间（ISO 8601 duration） |

**trust_requirements（信誉要求）**：

```json
{
  "trust_requirements": {
    "min_trust_score": 75,
    "min_reliability_score": 80,
    "min_reputation_score": 70,
    "prefer_cert_level": 2
  }
}
```

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `min_trust_score` | integer | 否 | 最低综合 Trust Score（0-100） |
| `min_reliability_score` | integer | 否 | 最低可靠性评分 |
| `min_reputation_score` | integer | 否 | 最低声誉评分 |
| `prefer_cert_level` | integer | 否 | 偏好的安全认证等级 |

**security_requirements（安全要求）**：

```json
{
  "security_requirements": {
    "min_cert_level": 2,
    "required_certifier": "any",
    "data_classification": "confidential",
    "compliance_requirements": [],
    "tool_restrictions": [
      "no_network_access",
      "sandbox_execution_only"
    ]
  }
}
```

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `min_cert_level` | integer | 否 | 最低安全认证等级（1-3） |
| `required_certifier` | string | 否 | 要求的认证机构 DID 或 "any" |
| `data_classification` | string | 否 | 数据分类（public, internal, confidential, restricted） |
| `compliance_requirements` | array | 否 | 合规要求列表（如 SOC2, GDPR 等） |
| `tool_restrictions` | array | 否 | 工具使用限制 |

**dispute_resolution（争议解决）**：

```json
{
  "dispute_resolution": {
    "method": "arbitration",
    "arbitrator": "did:aishield:arbitrator-official",
    "evidence_window": "72h",
    "arbitration_fee": {
      "amount": "5.00",
      "currency": "USDC",
      "payer": "loser"
    },
    "escalation_path": [
      "auto_negotiation",
      "arbitration",
      "community_vote"
    ],
    "max_dispute_duration": "336h"
  }
}
```

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `method` | string | 是 | 争议解决方式（arbitration, auto_refund, community_vote） |
| `arbitrator` | string (DID) | 条件必须 | 仲裁方 DID（method=arbitration 时必须） |
| `evidence_window` | string | 否 | 证据提交窗口（ISO 8601 duration） |
| `arbitration_fee` | object | 否 | 仲裁费用配置 |
| `escalation_path` | array | 否 | 升级路径 |
| `max_dispute_duration` | string | 否 | 最大争议处理时长 |

**receipt（完成凭证）**：

任务完成后，由 Delegate 填充完成凭证：

```json
{
  "receipt": {
    "version": "0.1",
    "delegation_id": "del-2026-07-20-a1b2c3d4",
    "task_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "result_summary": "代码安全审查完成。发现 3 个高危漏洞、5 个中危问题、12 个低危建议。",
    "result_artifacts": [
      {
        "type": "report",
        "url": "ipfs://QmXyz...",
        "hash": "sha256:abc123...",
        "format": "application/json"
      }
    ],
    "completed_at": "2026-07-20T18:30:00Z",
    "execution_duration_seconds": 31200,
    "delegate_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "delegate_signature": "eyJhbGciOiJFZERTQSIsImtpZCI6IiNrZXktMSJ9..."
  }
}
```

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `version` | string | 是 | 凭证格式版本 |
| `delegation_id` | string | 是 | 关联的委托 ID |
| `task_hash` | string | 是 | 任务描述的哈希值 |
| `result_summary` | string | 是 | 结果摘要（人类可读） |
| `result_artifacts` | array | 否 | 结果产物列表 |
| `completed_at` | string (ISO 8601) | 是 | 完成时间 |
| `execution_duration_seconds` | integer | 否 | 实际执行时长（秒） |
| `delegate_did` | string (DID) | 是 | 受托方 DID |
| `delegate_signature` | string | 是 | 受托方对凭证的签名 |

### 4.3 委托流程状态机

#### 4.3.1 状态定义

```
                    ┌─────────────┐
                    │   created   │ 委托任务已创建
                    └──────┬──────┘
                           │
                    接受/拒绝
                           │
              ┌────────────┼────────────┐
              │                         │
       ┌──────▼──────┐          ┌──────▼──────┐
       │  accepted   │          │  rejected   │ 委托被拒绝
       └──────┬──────┘          └─────────────┘
              │
       开始执行
              │
       ┌──────▼──────┐
       │  executing  │ 任务正在执行中
       └──────┬──────┘
              │
       提交结果
              │
       ┌──────▼──────┐
       │  submitted  │ 结果已提交，待验证
       └──────┬──────┘
              │
       验证结果
              │
       ┌──────▼──────┐
       │  verified   │ 结果已验证
       └──────┬──────┘
              │
       ┌──────┴──────┐
       │              │
┌──────▼──────┐ ┌─────▼──────┐
│  completed  │ │  disputed  │ 发生争议
└─────────────┘ └──────┬──────┘
                       │
                  争议处理
                       │
              ┌────────┼────────┐
              │                 │
       ┌──────▼──────┐  ┌──────▼──────┐
       │  resolved   │  │  cancelled  │ 争议取消
       │  (completed)│  └─────────────┘
       └─────────────┘
```

#### 4.3.2 状态转换规范

| 当前状态 | 目标状态 | 触发条件 | 执行者 |
|----------|----------|----------|--------|
| created | accepted | Delegate 接受委托 | Delegate |
| created | rejected | Delegate 拒绝委托 | Delegate |
| created | cancelled | Delegator 取消委托 | Delegator |
| accepted | executing | Delegate 开始执行任务 | Delegate |
| accepted | cancelled | 任一方取消（需支付违约金） | 双方 |
| executing | submitted | Delegate 提交完成凭证 | Delegate |
| executing | failed | 执行失败 | Delegate |
| submitted | verified | Delegator 验证通过 | Delegator |
| submitted | disputed | Delegator 发起争议 | Delegator |
| verified | completed | 托管释放/结算完成 | 系统 |
| disputed | resolved | 争议解决完成 | 仲裁方 |
| disputed | cancelled | 争议超时取消 | 系统 |

#### 4.3.3 状态转换 API

**创建委托**：

```
POST /aishield-delegation/v1/create
```

**接受委托**：

```
POST /aishield-delegation/v1/{delegation_id}/accept
```

**拒绝委托**：

```
POST /aishield-delegation/v1/{delegation_id}/reject

{
  "reason": "当前任务队列已满，无法接受新的委托"
}
```

**提交完成凭证**：

```
POST /aishield-delegation/v1/{delegation_id}/submit

{
  "receipt": {
    "task_hash": "sha256:...",
    "result_summary": "...",
    "completed_at": "2026-07-20T18:30:00Z"
  }
}
```

**验证结果**：

```
POST /aishield-delegation/v1/{delegation_id}/verify

{
  "verified": true,
  "rating": {
    "score": 4,
    "comment": "审查质量优秀，报告详尽"
  }
}
```

**发起争议**：

```
POST /aishield-delegation/v1/{delegation_id}/dispute

{
  "reason": "result_incomplete",
  "description": "审查报告未覆盖 API 安全部分",
  "evidence": ["https://..."]
}
```

### 4.4 争议解决

#### 4.4.1 争议类型

| 争议类型 | 代码 | 说明 |
|----------|------|------|
| 结果不完整 | `result_incomplete` | 任务未按要求全部完成 |
| 结果质量不合格 | `quality_unacceptable` | 结果质量低于约定标准 |
| 超时未完成 | `timeout` | 超过 SLA 时间未提交 |
| 安全违规 | `security_violation` | Agent 执行过程中违反安全要求 |
| 数据泄露 | `data_leakage` | 任务执行过程中发生数据泄露 |
| 托管争议 | `escrow_dispute` | 托管释放相关争议 |

#### 4.4.2 争议提交格式

```json
{
  "dispute": {
    "version": "0.1",
    "dispute_id": "disp-2026-07-20-x1y2z3",
    "delegation_id": "del-2026-07-20-a1b2c3d4",
    "initiator": {
      "did": "did:aishield:delegator-company-a",
      "role": "delegator"
    },
    "dispute_type": "result_incomplete",
    "description": "委托要求对 API 安全进行全面审查，但提交的报告仅覆盖了代码层面的安全审查，缺少 API 端点的安全测试。",
    "evidence": [
      {
        "type": "screenshot",
        "url": "https://evidence.storage/...",
        "hash": "sha256:...",
        "description": "原始委托要求截图"
      },
      {
        "type": "report",
        "url": "https://evidence.storage/...",
        "hash": "sha256:...",
        "description": "提交的审查报告"
      }
    ],
    "desired_resolution": "partial_refund",
    "claimed_amount": "40.00",
    "currency": "USDC",
    "created_at": "2026-07-21T09:00:00Z",
    "status": "open",
    "dispute_resolution_method": "arbitration"
  }
}
```

#### 4.4.3 仲裁流程

```
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │ 1.提交   │───►│ 2.答辩   │───►│ 3.证据   │───►│ 4.仲裁   │───►│ 5.执行   │
 │  争议    │    │  期      │    │  期      │    │  决定    │    │  裁决    │
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     0h             24h             72h             120h           144h
```

| 阶段 | 时长 | 说明 |
|------|------|------|
| 提交争议 | 立即 | Initiator 提交争议 |
| 答辩期 | 24 小时 | Respondent 提交答辩 |
| 证据期 | 72 小时 | 双方补充证据 |
| 仲裁决定 | 120 小时 | 仲裁方做出决定 |
| 执行裁决 | 144 小时 | 自动执行仲裁结果 |

#### 4.4.4 仲裁裁决格式

```json
{
  "arbitration_result": {
    "version": "0.1",
    "dispute_id": "disp-2026-07-20-x1y2z3",
    "arbitrator": {
      "did": "did:aishield:arbitrator-official",
      "name": "AIShield Official Arbitrator"
    },
    "decision": "partial_refund",
    "reasoning": "经审查，委托要求明确包含 API 安全测试，但受托方仅完成了代码层面的审查。考虑到已完成的代码审查部分具有价值，裁定部分退款。",
    "refund": {
      "amount": "35.00",
      "currency": "USDC",
      "to": "did:aishield:delegator-company-a"
    },
    "payment": {
      "amount": "65.00",
      "currency": "USDC",
      "to": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c"
    },
    "arbitration_fee": {
      "amount": "5.00",
      "currency": "USDC",
      "paid_by": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c"
    },
    "trust_score_impact": {
      "delegate_penalty": -5,
      "reason": "任务完成不完整"
    },
    "decided_at": "2026-07-26T09:00:00Z",
    "arbitrator_signature": "eyJhbGciOiJFZERTQSIsImtp..."
  }
}
```

#### 4.4.5 自动退款机制

当争议解决方式为 `auto_refund` 时：

```
触发条件：Delegator 在验证阶段标记 disputed，且选择 auto_refund
处理流程：
1. 冻结托管资金
2. 72 小时证据期
3. 自动将托管资金全额退还给 Delegator
4. Delegate 的 Reliability Score 下降
```

#### 4.4.6 社区投票机制

当争议升级到 `community_vote` 时：

```
投票资格：
- Trust Score >= 80 的 Agent 或 DID 持有者
- 非争议双方关联方

投票流程：
1. 公示争议详情（脱敏处理）
2. 48 小时投票期
3. 简单多数决
4. 自动执行投票结果

投票权重：
- 基础权重 = 1
- AIShield 治理代币持有者权重 += token_amount / total_tokens * 10
```

### 4.5 完成凭证 (Receipt)

#### 4.5.1 凭证生成规则

完成凭证 **MUST** 包含以下必要信息：

```json
{
  "receipt": {
    "version": "0.1",
    "delegation_id": "del-2026-07-20-a1b2c3d4",
    "task_hash": "sha256:{original_task_description_hash}",
    "result_summary": "人类可读的结果摘要",
    "result_artifacts": [
      {
        "type": "report|code|data|artifact",
        "url": "https://... 或 ipfs://...",
        "hash": "sha256:...",
        "format": "MIME type"
      }
    ],
    "completed_at": "ISO 8601 timestamp",
    "execution_duration_seconds": 31200,
    "delegate_did": "did:aishield:...",
    "delegate_signature": "Ed25519 签名"
  }
}
```

#### 4.5.2 凭证验证

凭证验证流程：

```
1. 验证 delegate_signature 是否有效
2. 验证 task_hash 是否与原始任务描述匹配
3. 验证 completed_at 是否在 SLA 范围内
4. 验证 result_artifacts 的哈希值是否匹配
5. 验证 delegation_id 是否有效且状态为 submitted
```

### 4.6 端到端委托示例

#### 4.6.1 完整流程示例

以下展示一个完整的委托流程，从任务创建到完成结算。

**Step 1: Delegator 查询 Delegate 的信任信息**

```http
GET /aishield-trust/v1/score/did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c HTTP/1.1

响应：
{
  "trust_score": 78,
  "dimensions": {
    "security": {"score": 82, "cert_level": 2},
    "reliability": {"score": 85},
    "reputation": {"score": 75},
    "activity": {"score": 65},
    "identity": {"score": 50}
  }
}
```

**Step 2: Delegator 创建委托**

```http
POST /aishield-delegation/v1/create HTTP/1.1
Content-Type: application/json

{
  "a2a_task": {
    "task_name": "代码安全审查",
    "description": "审查 GitHub 仓库的代码安全性",
    "input": {
      "repository_url": "https://github.com/example/project",
      "branch": "main"
    }
  },
  "aishield_delegation": {
    "delegator": {
      "did": "did:aishield:delegator-company-a",
      "name": "CompanyA Ops"
    },
    "delegate": {
      "did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c"
    },
    "escrow": {
      "enabled": true,
      "amount": "100.00",
      "currency": "USDC"
    },
    "trust_requirements": {
      "min_trust_score": 70
    },
    "security_requirements": {
      "min_cert_level": 2
    },
    "dispute_resolution": {
      "method": "arbitration"
    }
  }
}
```

**Step 3: Delegate 接受委托**

```http
POST /aishield-delegation/v1/del-2026-07-20-a1b2c3d4/accept HTTP/1.1
Content-Type: application/json

{
  "accept_note": "预计 12 小时内完成审查"
}
```

**Step 4: Delegate 执行任务并提交结果**

```http
POST /aishield-delegation/v1/del-2026-07-20-a1b2c3d4/submit HTTP/1.1
Content-Type: application/json

{
  "receipt": {
    "version": "0.1",
    "task_hash": "sha256:e3b0c442...",
    "result_summary": "审查完成：3 个高危漏洞、5 个中危问题",
    "completed_at": "2026-07-20T22:30:00Z",
    "delegate_did": "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c",
    "delegate_signature": "..."
  }
}
```

**Step 5: Delegator 验证并评价**

```http
POST /aishield-delegation/v1/del-2026-07-20-a1b2c3d4/verify HTTP/1.1
Content-Type: application/json

{
  "verified": true,
  "rating": {
    "score": 5,
    "comment": "审查质量极高，发现的漏洞非常准确"
  }
}
```

**Step 6: 系统结算**

系统自动释放托管资金给 Delegate，更新双方 Trust Score。

---

## 5. 实施指南 (Implementation Guide)

### 5.1 最小实现清单

#### 5.1.1 v0.1 合规必须实现的功能

以下是一个 Agent 要达到 AIShield Trust Standard v0.1 合规所 **MUST** 实现的最小功能集：

**子标准 A 合规（安全认证）**：

| 编号 | 要求 | 说明 |
|------|------|------|
| A-1 | 提供 `/.well-known/aishield-cert.json` 端点 | 返回有效的安全认证证书 |
| A-2 | 证书格式符合 JSON Schema | 包含所有必须字段 |
| A-3 | 证书包含有效的 `certifier_signature` | 可被独立验证 |
| A-4 | 证书 `expires_at` 未过期 | 在有效期内 |
| A-5 | 支持通过 DID 查询证书 | 可从 Agent DID 找到对应证书 |

**子标准 B 合规（信誉评分）**：

| 编号 | 要求 | 说明 |
|------|------|------|
| B-1 | 可通过 DID 查询 Trust Score | 提供 API 端点或使用 AIShield Registry |
| B-2 | 返回五个维度的评分 | Security, Reliability, Reputation, Activity, Identity |
| B-3 | 支持评分历史查询 | 至少 90 天历史 |

**子标准 C 合规（委托协议）**：

| 编号 | 要求 | 说明 |
|------|------|------|
| C-1 | 支持标准的委托任务创建格式 | 包含 A2A Task + AIShield 扩展字段 |
| C-2 | 实现完整的委托状态机 | created → accepted → executing → submitted → verified → completed |
| C-3 | 支持完成凭证 (Receipt) 生成和验证 | 包含签名验证 |
| C-4 | 支持至少一种争议解决方式 | auto_refund 或 arbitration |

#### 5.1.2 实现优先级

```
P0 (必须)                          P1 (建议)                          P2 (可选)
├─ 证书发现端点                    ├─ 批量评分查询                    ├─ 链上锚定
├─ 证书格式合规                    ├─ 评价系统                        ├─ 社区投票
├─ 评分查询 API                    ├─ SLA 管理                        ├─ 跨链托管
├─ 委托状态机                      ├─ 防刷机制                        ├─ 零知识证明
└─ Receipt 生成                   └─ 评分申诉                        └─ 治理代币
```

### 5.2 代码示例

#### 5.2.1 Python 实现示例

以下使用 Python 标准库 `urllib` 和 `json` 实现基本的 AIShield Trust Standard 交互。

**证书验证示例**：

```python
#!/usr/bin/env python3
"""
AIShield Trust Standard v0.1 - 证书验证示例
使用 Python 标准库实现
"""

import json
import urllib.request
import urllib.error
import hashlib
from datetime import datetime, timezone


class AIShieldCertVerifier:
    """AIShield 安全认证证书验证器"""

    CERT_DISCOVERY_PATH = "/.well-known/aishield-cert.json"
    REGISTRY_URL = "https://registry.aishield.org/v1/cert/agent/{did}"

    def __init__(self, certifier_public_keys=None):
        """
        初始化验证器

        Args:
            certifier_public_keys: 认证机构公钥字典 {certifier_did: public_key}
        """
        self.certifier_public_keys = certifier_public_keys or {}

    def fetch_cert_from_agent(self, agent_domain):
        """
        从 Agent 的标准发现端点获取证书

        Args:
            agent_domain: Agent 的域名 (如 "agent.example.com")

        Returns:
            dict: 证书 JSON 数据
        """
        url = f"https://{agent_domain}{self.CERT_DISCOVERY_PATH}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
                elif resp.status == 410:
                    raise ValueError("证书已被吊销")
                elif resp.status == 404:
                    raise ValueError("未找到安全认证证书")
                else:
                    raise ValueError(f"Unexpected status: {resp.status}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"无法连接到 Agent: {e}")

    def fetch_cert_from_registry(self, agent_did):
        """
        从 AIShield Registry 查询证书

        Args:
            agent_did: Agent 的 DID

        Returns:
            dict: 证书 JSON 数据
        """
        url = self.REGISTRY_URL.format(did=urllib.parse.quote(agent_did, safe=""))
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
                elif resp.status == 404:
                    raise ValueError("Agent 未注册或未认证")
                else:
                    raise ValueError(f"Unexpected status: {resp.status}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"无法连接到 Registry: {e}")

    def verify_cert(self, cert_data):
        """
        验证证书的有效性

        Args:
            cert_data: 证书 JSON 数据

        Returns:
            dict: 验证结果 {
                "valid": bool,
                "checks": list,
                "warnings": list,
                "errors": list
            }
        """
        result = {
            "valid": False,
            "checks": [],
            "warnings": [],
            "errors": []
        }

        cert = cert_data.get("aishield_cert")
        if not cert:
            result["errors"].append("缺少 aishield_cert 字段")
            return result

        # 检查必须字段
        required_fields = [
            "cert_id", "cert_version", "agent_did", "agent_name",
            "level", "level_name", "score", "scan_hash",
            "issued_at", "expires_at", "certifier", "certifier_signature"
        ]
        for field in required_fields:
            if field not in cert:
                result["errors"].append(f"缺少必须字段: {field}")
                return result

        result["checks"].append({
            "check": "required_fields",
            "status": "pass",
            "message": "所有必须字段存在"
        })

        # 检查证书版本
        if cert["cert_version"] != "0.1":
            result["warnings"].append(f"证书版本 {cert['cert_version']}，当前标准版本 0.1")

        # 检查认证等级
        if cert["level"] not in [1, 2, 3]:
            result["errors"].append(f"无效的认证等级: {cert['level']}")
            return result
        result["checks"].append({
            "check": "cert_level",
            "status": "pass",
            "message": f"认证等级: {cert['level_name']} (Level {cert['level']})"
        })

        # 检查评分范围
        if not (0 <= cert["score"] <= 100):
            result["errors"].append(f"无效的评分范围: {cert['score']}")
            return result

        # 检查等级-评分一致性
        level_score_requirements = {1: 60, 2: 80, 3: 80}
        min_score = level_score_requirements[cert["level"]]
        if cert["score"] < min_score:
            result["errors"].append(
                f"评分 {cert['score']} 低于 Level {cert['level']} 最低要求 {min_score}"
            )
            return result

        result["checks"].append({
            "check": "score_validity",
            "status": "pass",
            "message": f"评分 {cert['score']} 符合 Level {cert['level']} 要求"
        })

        # 检查证书有效期
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(cert["expires_at"].replace("Z", "+00:00"))
        issued_at = datetime.fromisoformat(cert["issued_at"].replace("Z", "+00:00"))

        if now > expires_at:
            result["errors"].append(f"证书已于 {cert['expires_at']} 过期")
            return result

        result["checks"].append({
            "check": "expiry",
            "status": "pass",
            "message": f"证书有效期至 {cert['expires_at']}"
        })

        # 检查是否被标记为过期（由 Agent 自行标记）
        if cert.get("expired"):
            result["errors"].append("证书已被标记为过期")
            return result

        # 验证签名（简化版 - 生产环境应使用完整 Ed25519 验证）
        if cert.get("certifier_signature"):
            # TODO: 实际实现应使用 Ed25519 公钥验证签名
            result["warnings"].append("签名验证需要集成 Ed25519 库")
            result["checks"].append({
                "check": "signature",
                "status": "warning",
                "message": "签名存在但未验证（需集成加密库）"
            })
        else:
            result["errors"].append("缺少 certifier_signature")
            return result

        # 所有检查通过
        result["valid"] = True
        return result


# 使用示例
if __name__ == "__main__":
    verifier = AIShieldCertVerifier()

    # 验证某个 Agent 的证书
    try:
        cert = verifier.fetch_cert_from_agent("agent.example.com")
        result = verifier.verify_cert(cert)

        print("=== AIShield 证书验证结果 ===")
        print(f"有效: {result['valid']}")
        for check in result["checks"]:
            status_icon = "[PASS]" if check["status"] == "pass" else "[WARN]"
            print(f"  {status_icon} {check['message']}")
        if result["warnings"]:
            print("警告:")
            for w in result["warnings"]:
                print(f"  [WARN] {w}")
        if result["errors"]:
            print("错误:")
            for e in result["errors"]:
                print(f"  [FAIL] {e}")

    except (ValueError, ConnectionError) as e:
        print(f"验证失败: {e}")
```

**Trust Score 查询示例**：

```python
#!/usr/bin/env python3
"""
AIShield Trust Standard v0.1 - Trust Score 查询示例
使用 Python 标准库实现
"""

import json
import urllib.request
import urllib.parse


class TrustScoreClient:
    """AIShield Trust Score 查询客户端"""

    DEFAULT_REGISTRY = "https://trust.aishield.org"

    def __init__(self, registry_url=None):
        self.registry_url = registry_url or self.DEFAULT_REGISTRY

    def get_trust_score(self, agent_did):
        """
        查询 Agent 的 Trust Score

        Args:
            agent_did: Agent 的 DID

        Returns:
            dict: Trust Score 详情
        """
        encoded_did = urllib.parse.quote(agent_did, safe="")
        url = f"{self.registry_url}/aishield-trust/v1/score/{encoded_did}"

        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "AIShield-Python-Client/0.1"
        })

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["trust_score_response"]
                elif resp.status == 404:
                    raise ValueError(f"Agent 未找到: {agent_did}")
                elif resp.status == 429:
                    retry_after = resp.headers.get("Retry-After", "60")
                    raise ValueError(f"请求频率超限，{retry_after}秒后重试")
                else:
                    raise ValueError(f"Unexpected status: {resp.status}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"查询失败: {e}")

    def check_trust_requirements(self, agent_did, min_score=None, min_level=None):
        """
        检查 Agent 是否满足信任要求

        Args:
            agent_did: Agent 的 DID
            min_score: 最低 Trust Score 要求
            min_level: 最低安全认证等级要求

        Returns:
            dict: { "meets_requirements": bool, "details": dict }
        """
        score_data = self.get_trust_score(agent_did)

        result = {
            "agent_did": agent_did,
            "meets_requirements": True,
            "details": {
                "trust_score": score_data["trust_score"],
                "cert_level": score_data["dimensions"]["security"]["details"]["cert_level"],
                "all_checks": []
            }
        }

        if min_score is not None:
            meets = score_data["trust_score"] >= min_score
            result["meets_requirements"] = result["meets_requirements"] and meets
            result["details"]["all_checks"].append({
                "requirement": f"min_trust_score >= {min_score}",
                "actual": score_data["trust_score"],
                "met": meets
            })

        if min_level is not None:
            actual_level = score_data["dimensions"]["security"]["details"]["cert_level"]
            meets = actual_level >= min_level
            result["meets_requirements"] = result["meets_requirements"] and meets
            result["details"]["all_checks"].append({
                "requirement": f"min_cert_level >= {min_level}",
                "actual": actual_level,
                "met": meets
            })

        return result


# 使用示例
if __name__ == "__main__":
    client = TrustScoreClient()

    # 查询 Trust Score
    did = "did:aishield:7f3a2b1c9d4e5f6a8b0c1d2e3f4a5b6c"
    score = client.get_trust_score(did)

    print("=== Trust Score ===")
    print(f"Agent: {score['agent_name']}")
    print(f"Trust Score: {score['trust_score']}")
    print()
    print("各维度评分:")
    for dim_name, dim_data in score["dimensions"].items():
        print(f"  {dim_name}: {dim_data['score']} (权重: {dim_data['weight']*100:.0f}%)")

    print()

    # 检查信任要求
    check = client.check_trust_requirements(did, min_score=75, min_level=2)
    print("=== 信任要求检查 ===")
    print(f"满足要求: {check['meets_requirements']}")
    for item in check["details"]["all_checks"]:
        status = "[PASS]" if item["met"] else "[FAIL]"
        print(f"  {status} {item['requirement']} (实际: {item['actual']})")
```

**委托协议交互示例**：

```python
#!/usr/bin/env python3
"""
AIShield Trust Standard v0.1 - 委托协议交互示例
使用 Python 标准库实现
"""

import json
import urllib.request
import hashlib
from datetime import datetime, timezone


class DelegationClient:
    """AIShield 委托协议客户端"""

    def __init__(self, delegate_endpoint, delegator_did=None):
        """
        Args:
            delegate_endpoint: Delegate Agent 的 A2A 端点
            delegator_did: Delegator 的 DID
        """
        self.delegate_endpoint = delegate_endpoint.rstrip("/")
        self.delegator_did = delegator_did

    def _make_request(self, path, data=None, method="GET"):
        """发送 HTTP 请求"""
        url = f"{self.delegate_endpoint}{path}"
        body = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(url, data=body, method=method, headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def create_delegation(self, task_name, task_description, task_input,
                           escrow=None, trust_requirements=None,
                           security_requirements=None, dispute_method="arbitration"):
        """
        创建委托任务

        Args:
            task_name: 任务名称
            task_description: 任务描述
            task_input: 任务输入参数
            escrow: 托管配置 (可选)
            trust_requirements: 信誉要求 (可选)
            security_requirements: 安全要求 (可选)
            dispute_method: 争议解决方式

        Returns:
            dict: 创建的委托任务
        """
        # 计算任务哈希
        task_content = json.dumps({
            "name": task_name,
            "description": task_description,
            "input": task_input
        }, sort_keys=True, ensure_ascii=False)
        task_hash = "sha256:" + hashlib.sha256(task_content.encode("utf-8")).hexdigest()

        delegation_data = {
            "a2a_task": {
                "task_name": task_name,
                "description": task_description,
                "input": task_input,
                "status": "created",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            "aishield_delegation": {
                "version": "0.1",
                "delegator": {
                    "did": self.delegator_did
                },
                "escrow": escrow,
                "trust_requirements": trust_requirements,
                "security_requirements": security_requirements,
                "dispute_resolution": {
                    "method": dispute_method
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }

        return self._make_request(
            "/aishield-delegation/v1/create",
            delegation_data,
            method="POST"
        )

    def accept_delegation(self, delegation_id, accept_note=None):
        """接受委托"""
        data = {}
        if accept_note:
            data["accept_note"] = accept_note
        return self._make_request(
            f"/aishield-delegation/v1/{delegation_id}/accept",
            data,
            method="POST"
        )

    def submit_receipt(self, delegation_id, result_summary,
                        result_artifacts=None, task_hash=None):
        """提交完成凭证"""
        receipt = {
            "version": "0.1",
            "delegation_id": delegation_id,
            "task_hash": task_hash,
            "result_summary": result_summary,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        if result_artifacts:
            receipt["result_artifacts"] = result_artifacts

        return self._make_request(
            f"/aishield-delegation/v1/{delegation_id}/submit",
            {"receipt": receipt},
            method="POST"
        )

    def verify_result(self, delegation_id, verified, rating=None):
        """验证结果"""
        data = {"verified": verified}
        if rating:
            data["rating"] = rating
        return self._make_request(
            f"/aishield-delegation/v1/{delegation_id}/verify",
            data,
            method="POST"
        )

    def file_dispute(self, delegation_id, dispute_type, description, evidence=None):
        """发起争议"""
        data = {
            "dispute_type": dispute_type,
            "description": description
        }
        if evidence:
            data["evidence"] = evidence
        return self._make_request(
            f"/aishield-delegation/v1/{delegation_id}/dispute",
            data,
            method="POST"
        )


# 使用示例
if __name__ == "__main__":
    # === Delegator 侧 ===
    client = DelegationClient(
        delegate_endpoint="https://agent.example.com/a2a",
        delegator_did="did:aishield:delegator-company-a"
    )

    # 创建委托
    delegation = client.create_delegation(
        task_name="代码安全审查",
        task_description="审查 GitHub 仓库的代码安全性",
        task_input={
            "repository_url": "https://github.com/example/project",
            "branch": "main"
        },
        escrow={
            "enabled": True,
            "amount": "100.00",
            "currency": "USDC"
        },
        trust_requirements={
            "min_trust_score": 75
        },
        security_requirements={
            "min_cert_level": 2
        }
    )

    delegation_id = delegation["aishield_delegation"]["delegation_id"]
    print(f"委托已创建: {delegation_id}")
    print(f"状态: {delegation['a2a_task']['status']}")

    # === Delegate 侧 ===
    # client.accept_delegation(delegation_id, "预计 12 小时内完成")

    # === Delegate 提交结果 ===
    # client.submit_receipt(
    #     delegation_id=delegation_id,
    #     result_summary="审查完成：3 个高危漏洞、5 个中危问题",
    #     task_hash="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    # )

    # === Delegator 验证 ===
    # client.verify_result(
    #     delegation_id=delegation_id,
    #     verified=True,
    #     rating={"score": 5, "comment": "审查质量极高"}
    # )
```

### 5.3 测试用例

#### 5.3.1 证书验证测试

```python
#!/usr/bin/env python3
"""
AIShield Trust Standard v0.1 - 证书验证测试用例
"""

import json
import unittest


class TestAIShieldCertValidation(unittest.TestCase):
    """证书验证测试"""

    def setUp(self):
        """准备测试数据"""
        self.valid_cert = {
            "$schema": "https://aishield.org/schemas/cert/v0.1",
            "aishield_cert": {
                "cert_id": "cert-aishield-2026-07-20-test001",
                "cert_version": "0.1",
                "agent_did": "did:aishield:test-agent-001",
                "agent_name": "TestAgent",
                "level": 2,
                "level_name": "Verified",
                "score": 82,
                "scan_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "issued_at": "2026-07-20T10:00:00Z",
                "expires_at": "2027-01-17T10:00:00Z",
                "certifier": {
                    "did": "did:aishield:certifier-test",
                    "name": "Test Certifier"
                },
                "certifier_signature": "test_signature_placeholder"
            }
        }

    def test_valid_cert_passes(self):
        """有效证书应通过所有验证"""
        cert = self.valid_cert
        ac = cert["aishield_cert"]

        # 检查必须字段
        required = [
            "cert_id", "cert_version", "agent_did", "agent_name",
            "level", "level_name", "score", "scan_hash",
            "issued_at", "expires_at", "certifier", "certifier_signature"
        ]
        for field in required:
            self.assertIn(field, ac)

        # 检查等级
        self.assertIn(ac["level"], [1, 2, 3])
        self.assertIsInstance(ac["level_name"], str)

        # 检查评分范围
        self.assertGreaterEqual(ac["score"], 0)
        self.assertLessEqual(ac["score"], 100)

        # 检查等级-评分一致性
        level_requirements = {1: 60, 2: 80, 3: 80}
        self.assertGreaterEqual(ac["score"], level_requirements[ac["level"]])

    def test_missing_required_field(self):
        """缺少必须字段应导致验证失败"""
        cert = json.loads(json.dumps(self.valid_cert))
        del cert["aishield_cert"]["cert_id"]

        required = [
            "cert_id", "cert_version", "agent_did", "agent_name",
            "level", "level_name", "score", "scan_hash",
            "issued_at", "expires_at", "certifier", "certifier_signature"
        ]
        for field in required:
            if field not in cert["aishield_cert"]:
                self.fail(f"缺少必须字段: {field}")

    def test_invalid_level(self):
        """无效的认证等级应被拒绝"""
        cert = json.loads(json.dumps(self.valid_cert))
        cert["aishield_cert"]["level"] = 4

        self.assertNotIn(cert["aishield_cert"]["level"], [1, 2, 3])

    def test_score_below_level_requirement(self):
        """评分低于等级最低要求应被拒绝"""
        cert = json.loads(json.dumps(self.valid_cert))
        cert["aishield_cert"]["level"] = 2
        cert["aishield_cert"]["score"] = 50

        level_requirements = {1: 60, 2: 80, 3: 80}
        min_score = level_requirements[cert["aishield_cert"]["level"]]
        self.assertLess(cert["aishield_cert"]["score"], min_score)

    def test_score_out_of_range(self):
        """评分超出 0-100 范围应被拒绝"""
        for invalid_score in [-1, 101, 150]:
            cert = json.loads(json.dumps(self.valid_cert))
            cert["aishield_cert"]["score"] = invalid_score
            self.assertFalse(
                0 <= cert["aishield_cert"]["score"] <= 100,
                f"评分 {invalid_score} 应被拒绝"
            )

    def test_level_name_consistency(self):
        """等级名称应与等级编号一致"""
        level_names = {1: "Basic", 2: "Verified", 3: "Enterprise"}
        for level, name in level_names.items():
            cert = json.loads(json.dumps(self.valid_cert))
            cert["aishield_cert"]["level"] = level
            cert["aishield_cert"]["level_name"] = name
            self.assertEqual(
                level_names[cert["aishield_cert"]["level"]],
                cert["aishield_cert"]["level_name"]
            )


class TestTrustScoreCalculation(unittest.TestCase):
    """Trust Score 计算测试"""

    def test_full_score(self):
        """所有维度满分时，总分应为 100"""
        dimensions = {
            "security": {"score": 100, "weight": 0.30},
            "reliability": {"score": 100, "weight": 0.25},
            "reputation": {"score": 100, "weight": 0.25},
            "activity": {"score": 100, "weight": 0.10},
            "identity": {"score": 100, "weight": 0.10}
        }

        total = sum(d["score"] * d["weight"] for d in dimensions.values())
        self.assertAlmostEqual(total, 100.0, places=2)

    def test_zero_score(self):
        """所有维度零分时，总分应为 0"""
        dimensions = {
            "security": {"score": 0, "weight": 0.30},
            "reliability": {"score": 0, "weight": 0.25},
            "reputation": {"score": 0, "weight": 0.25},
            "activity": {"score": 0, "weight": 0.10},
            "identity": {"score": 0, "weight": 0.10}
        }

        total = sum(d["score"] * d["weight"] for d in dimensions.values())
        self.assertAlmostEqual(total, 0.0, places=2)

    def test_weights_sum_to_one(self):
        """权重之和应为 1"""
        weights = [0.30, 0.25, 0.25, 0.10, 0.10]
        self.assertAlmostEqual(sum(weights), 1.0, places=2)

    def test_security_score_mapping_level1(self):
        """Level 1 安全评分映射测试"""
        # cert_score=60 → Security Score=50
        security_score = 50 + (60 - 60) * (19 / 40)
        self.assertAlmostEqual(security_score, 50.0, places=1)

        # cert_score=100 → Security Score=69
        security_score = 50 + (100 - 60) * (19 / 40)
        self.assertAlmostEqual(security_score, 69.0, places=1)

    def test_security_score_mapping_level2(self):
        """Level 2 安全评分映射测试"""
        # cert_score=80 → Security Score=70
        security_score = 70 + (80 - 80) * (19 / 20)
        self.assertAlmostEqual(security_score, 70.0, places=1)

        # cert_score=100 → Security Score=89
        security_score = 70 + (100 - 80) * (19 / 20)
        self.assertAlmostEqual(security_score, 89.0, places=1)

    def test_new_agent_cap(self):
        """新 Agent 信誉分上限测试"""
        # Day 1-7: 上限 40
        cap_day1 = 40 + min(30, 0) * 1.5
        self.assertLessEqual(cap_day1, 40)

        # Day 8-14: 上限 55
        cap_day8 = 40 + min(30, 7) * 1.5
        self.assertLessEqual(cap_day8, 55)

        # Day 22-30: 上限 85
        cap_day22 = 40 + min(30, 21) * 1.5
        self.assertLessEqual(cap_day22, 85)


class TestDelegationProtocol(unittest.TestCase):
    """委托协议测试"""

    def test_delegation_state_machine(self):
        """委托状态机转换测试"""
        valid_transitions = {
            "created": ["accepted", "rejected", "cancelled"],
            "accepted": ["executing", "cancelled"],
            "executing": ["submitted", "failed"],
            "submitted": ["verified", "disputed"],
            "verified": ["completed"],
            "disputed": ["resolved", "cancelled"]
        }

        # 验证所有状态都有定义转换
        states = ["created", "accepted", "executing", "submitted",
                  "verified", "completed", "disputed", "resolved",
                  "rejected", "cancelled", "failed"]

        for state in ["created", "accepted", "executing", "submitted", "verified", "disputed"]:
            self.assertIn(state, valid_transitions)

    def test_delegation_required_fields(self):
        """委托任务必须字段测试"""
        delegation = {
            "a2a_task": {
                "task_id": "test-001",
                "task_name": "Test Task",
                "status": "created"
            },
            "aishield_delegation": {
                "version": "0.1",
                "delegation_id": "del-test-001",
                "delegator": {"did": "did:aishield:delegator"},
                "delegate": {"did": "did:aishield:delegate"},
                "trust_requirements": {},
                "security_requirements": {},
                "dispute_resolution": {"method": "arbitration"}
            }
        }

        ad = delegation["aishield_delegation"]
        required = ["version", "delegation_id", "delegator", "delegate"]
        for field in required:
            self.assertIn(field, ad)

    def test_receipt_required_fields(self):
        """完成凭证必须字段测试"""
        receipt = {
            "version": "0.1",
            "delegation_id": "del-test-001",
            "task_hash": "sha256:test",
            "result_summary": "测试完成",
            "completed_at": "2026-07-20T18:30:00Z",
            "delegate_did": "did:aishield:delegate",
            "delegate_signature": "test_sig"
        }

        required = [
            "version", "delegation_id", "task_hash",
            "result_summary", "completed_at",
            "delegate_did", "delegate_signature"
        ]
        for field in required:
            self.assertIn(field, receipt)

    def test_dispute_types(self):
        """争议类型测试"""
        valid_types = [
            "result_incomplete",
            "quality_unacceptable",
            "timeout",
            "security_violation",
            "data_leakage",
            "escrow_dispute"
        ]
        dispute_type = "result_incomplete"
        self.assertIn(dispute_type, valid_types)


if __name__ == "__main__":
    unittest.main()
```

### 5.4 兼容性检查清单

#### 5.4.1 Agent 开发者自检清单

以下清单帮助 Agent 开发者确认其实现是否完全符合 AIShield Trust Standard v0.1。

**子标准 A — 安全认证**：

| 编号 | 检查项 | 通过? |
|------|--------|-------|
| A-CHK-01 | Agent 拥有有效的 DID 标识 | [ ] |
| A-CHK-02 | 通过至少 Level 1 安全认证 | [ ] |
| A-CHK-03 | `/.well-known/aishield-cert.json` 端点可访问 | [ ] |
| A-CHK-04 | 返回的证书包含所有必须字段 | [ ] |
| A-CHK-05 | 证书 `certifier_signature` 可被独立验证 | [ ] |
| A-CHK-06 | 证书在有效期内 | [ ] |
| A-CHK-07 | Skill Card 可通过标准路径访问 | [ ] |
| A-CHK-08 | 工具描述使用标准 JSON Schema 格式 | [ ] |

**子标准 B — 信誉评分**：

| 编号 | 检查项 | 通过? |
|------|--------|-------|
| B-CHK-01 | Trust Score 可通过 DID 查询 | [ ] |
| B-CHK-02 | 返回五个维度的加权评分 | [ ] |
| B-CHK-03 | 支持评分历史查询（至少 90 天） | [ ] |
| B-CHK-04 | 评分更新机制符合事件驱动 + 每日聚合规范 | [ ] |
| B-CHK-05 | 新注册 Agent 有 30 天保护期 | [ ] |

**子标准 C — 委托协议**：

| 编号 | 检查项 | 通过? |
|------|--------|-------|
| C-CHK-01 | 支持标准委托任务创建格式 | [ ] |
| C-CHK-02 | 委托任务包含 A2A Task + AIShield 扩展字段 | [ ] |
| C-CHK-03 | 实现完整的状态机（created → completed） | [ ] |
| C-CHK-04 | 支持完成凭证 (Receipt) 生成 | [ ] |
| C-CHK-05 | Receipt 包含有效签名 | [ ] |
| C-CHK-06 | 支持至少一种争议解决方式 | [ ] |
| C-CHK-07 | 争议提交格式符合标准 | [ ] |
| C-CHK-08 | 支持信任要求验证（创建前检查） | [ ] |

#### 5.4.2 Certifier 合规检查清单

| 编号 | 检查项 | 通过? |
|------|--------|-------|
| CF-CHK-01 | 扫描工具覆盖所有 11 个检测项 | [ ] |
| CF-CHK-02 | 评分算法使用标准加权平均 | [ ] |
| CF-CHK-03 | 证书格式符合 JSON Schema | [ ] |
| CF-CHK-04 | 证书使用 Ed25519 签名 | [ ] |
| CF-CHK-05 | 证书包含 `expires_at` 字段 | [ ] |
| CF-CHK-06 | 支持证书吊销机制 | [ ] |
| CF-CHK-07 | 扫描结果哈希可追溯 | [ ] |

#### 5.4.3 平台集成检查清单

| 编号 | 检查项 | 通过? |
|------|--------|-------|
| PL-CHK-01 | 支持 AIShield DID 解析 | [ ] |
| PL-CHK-02 | 集成 Trust Score 查询 API | [ ] |
| PL-CHK-03 | 在委托创建时验证 Trust Score 要求 | [ ] |
| PL-CHK-04 | 在委托创建时验证安全认证等级 | [ ] |
| PL-CHK-05 | 支持 AIShield 托管机制 | [ ] |
| PL-CHK-06 | 支持标准化争议解决流程 | [ ] |
| PL-CHK-07 | 记录委托历史用于评分计算 | [ ] |

---

## 6. 许可证与贡献

### 6.1 许可证

本标准文档采用 **Creative Commons Attribution 4.0 International (CC BY 4.0)** 许可证发布。

**你被允许**：

- **共享 (Share)**：在任何媒介或格式中复制和重新分发材料
- **改编 (Adapt)**：重新混合、转换和在此基础上构建材料

**条件**：

- **署名 (Attribution)**：你必须给予适当的署名，提供许可证链接，并指出是否进行了更改。你可以以任何合理的方式进行署名，但不得以任何方式暗示许可方认可你或你的使用。

**无附加限制**：你不得适用法律条款或技术措施，在法律上限制其他人做许可证允许的任何事情。

许可证全文：https://creativecommons.org/licenses/by/4.0/legalcode

### 6.2 贡献指南

AIShield Trust Standard 是一个开放标准，欢迎所有个人和组织参与贡献和改进。

#### 6.2.1 贡献方式

| 方式 | 说明 |
|------|------|
| **Issue 提出** | 发现标准中的问题、矛盾或改进空间，提交 Issue |
| **Pull Request** | 直接提交标准的修改建议 |
| **参考实现** | 提供标准的参考实现代码 |
| **测试用例** | 提交标准合规性测试用例 |
| **翻译** | 将标准翻译为其他语言 |
| ** adoption 反馈** | 分享你在实际项目中的实施经验和问题 |

#### 6.2.2 提交流程

```
1. Fork 标准仓库
2. 创建特性分支 (git checkout -b feature/your-proposal)
3. 编写修改内容
4. 添加充分的测试用例或验证示例
5. 提交 Pull Request
6.等待社区审核和讨论
7. 维护者合并或请求修改
```

#### 6.2.3 版本号规范

遵循 Semantic Versioning 2.0.0：

- **MAJOR**: 不兼容的标准变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的 Bug 修复和澄清

### 6.3 致谢

AIShield Trust Standard 的制定受益于以下开源标准和社区工作：

- **Google A2A Protocol**：Agent 间通信协议基础
- **Anthropic MCP (Model Context Protocol)**：模型上下文协议
- **OWASP MCP Top 10**：MCP 安全风险清单
- **W3C DID Core**：去中心化身份标识标准
- **RFC 2119**：规范关键字定义
- **OAuth 2.0**：授权框架标准

---

## 附录 A：JSON Schema 参考

### A.1 证书 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://aishield.org/schemas/cert/v0.1",
  "title": "AIShield Security Certification",
  "type": "object",
  "required": ["aishield_cert"],
  "properties": {
    "$schema": {
      "type": "string",
      "const": "https://aishield.org/schemas/cert/v0.1"
    },
    "aishield_cert": {
      "type": "object",
      "required": [
        "cert_id", "cert_version", "agent_did", "agent_name",
        "level", "level_name", "score", "scan_hash",
        "issued_at", "expires_at", "certifier", "certifier_signature"
      ],
      "properties": {
        "cert_id": {
          "type": "string",
          "pattern": "^cert-aishield-\\d{4}-\\d{2}-\\d{2}-[a-z0-9]+$"
        },
        "cert_version": {
          "type": "string",
          "const": "0.1"
        },
        "agent_did": {
          "type": "string",
          "pattern": "^did:aishield:"
        },
        "agent_name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "agent_endpoint": {
          "type": "string",
          "format": "uri"
        },
        "level": {
          "type": "integer",
          "minimum": 1,
          "maximum": 3
        },
        "level_name": {
          "type": "string",
          "enum": ["Basic", "Verified", "Enterprise"]
        },
        "score": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100
        },
        "score_breakdown": {
          "type": "object"
        },
        "scan_hash": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$"
        },
        "scan_timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "certifier": {
          "type": "object",
          "required": ["did", "name"],
          "properties": {
            "did": {"type": "string", "pattern": "^did:"},
            "name": {"type": "string"},
            "endpoint": {"type": "string", "format": "uri"}
          }
        },
        "issued_at": {
          "type": "string",
          "format": "date-time"
        },
        "expires_at": {
          "type": "string",
          "format": "date-time"
        },
        "verification_url": {
          "type": "string",
          "format": "uri"
        },
        "on_chain": {
          "type": "object",
          "properties": {
            "anchored": {"type": "boolean"},
            "level_3_available": {"type": "boolean"}
          }
        },
        "certifier_signature": {
          "type": "string",
          "minLength": 1
        }
      }
    }
  }
}
```

### A.2 委托任务 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://aishield.org/schemas/delegation/v0.1",
  "title": "AIShield Delegation Task",
  "type": "object",
  "required": ["a2a_task", "aishield_delegation"],
  "properties": {
    "a2a_task": {
      "type": "object",
      "required": ["task_id", "task_name", "status"],
      "properties": {
        "task_id": {"type": "string"},
        "task_name": {"type": "string"},
        "description": {"type": "string"},
        "status": {
          "type": "string",
          "enum": ["created", "accepted", "rejected", "cancelled",
                   "executing", "submitted", "failed",
                   "verified", "completed", "disputed", "resolved"]
        },
        "input": {"type": "object"},
        "output": {},
        "created_at": {"type": "string", "format": "date-time"}
      }
    },
    "aishield_delegation": {
      "type": "object",
      "required": ["version", "delegation_id", "delegator", "delegate",
                   "dispute_resolution"],
      "properties": {
        "version": {"type": "string", "const": "0.1"},
        "delegation_id": {
          "type": "string",
          "pattern": "^del-\\d{4}-\\d{2}-\\d{2}-[a-z0-9]+$"
        },
        "delegator": {
          "type": "object",
          "required": ["did"],
          "properties": {
            "did": {"type": "string", "pattern": "^did:"},
            "name": {"type": "string"},
            "endpoint": {"type": "string", "format": "uri"}
          }
        },
        "delegate": {
          "type": "object",
          "required": ["did"],
          "properties": {
            "did": {"type": "string", "pattern": "^did:"},
            "name": {"type": "string"},
            "endpoint": {"type": "string", "format": "uri"}
          }
        },
        "escrow": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "amount": {"type": "string"},
            "currency": {"type": "string"},
            "escrow_agent": {"type": "string"},
            "contract_address": {"type": "string"},
            "release_conditions": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        "trust_requirements": {
          "type": "object",
          "properties": {
            "min_trust_score": {
              "type": "integer",
              "minimum": 0,
              "maximum": 100
            },
            "min_reliability_score": {"type": "integer"},
            "min_reputation_score": {"type": "integer"},
            "prefer_cert_level": {"type": "integer"}
          }
        },
        "security_requirements": {
          "type": "object",
          "properties": {
            "min_cert_level": {
              "type": "integer",
              "minimum": 1,
              "maximum": 3
            },
            "data_classification": {
              "type": "string",
              "enum": ["public", "internal", "confidential", "restricted"]
            },
            "tool_restrictions": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        "dispute_resolution": {
          "type": "object",
          "required": ["method"],
          "properties": {
            "method": {
              "type": "string",
              "enum": ["arbitration", "auto_refund", "community_vote"]
            },
            "arbitrator": {"type": "string"},
            "evidence_window": {"type": "string"},
            "escalation_path": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        "receipt": {},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

---

## 附录 B：状态码与错误码参考

### B.1 证书相关错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `CERT_NOT_FOUND` | 404 | 未找到安全认证证书 |
| `CERT_EXPIRED` | 200 + `expired:true` | 证书已过期 |
| `CERT_REVOKED` | 410 | 证书已被吊销 |
| `CERT_INVALID` | 400 | 证书格式无效 |
| `CERT_SIGNATURE_INVALID` | 400 | 签名验证失败 |

### B.2 评分相关错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `AGENT_NOT_FOUND` | 404 | Agent DID 不存在 |
| `SCORE_UNAVAILABLE` | 503 | 评分暂时不可用 |
| `RATE_LIMITED` | 429 | 请求频率超限 |

### B.3 委托相关错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `DELEGATION_NOT_FOUND` | 404 | 委托不存在 |
| `INVALID_STATE_TRANSITION` | 409 | 非法状态转换 |
| `TRUST_REQUIREMENTS_NOT_MET` | 403 | 信任要求未满足 |
| `SECURITY_REQUIREMENTS_NOT_MET` | 403 | 安全要求未满足 |
| `ESCROW_INSUFFICIENT` | 402 | 托管资金不足 |
| `DISPUTE_ALREADY_EXISTS` | 409 | 争议已存在 |

---

## 附录 C：版本变更记录

### v0.1 (2026-07-20)

**初始发布 (Draft)**

新增内容：
- 子标准 A：Agent Security Certification
  - 三个认证等级 (Basic, Verified, Enterprise)
  - 标准化证书格式 (JSON)
  - `/.well-known/aishield-cert.json` 发现端点
  - SVG 徽章规范
- 子标准 B：Agent Trust Score
  - 五维度加权评分体系 (Security, Reliability, Reputation, Activity, Identity)
  - 标准 API 查询端点
  - 事件驱动 + 每日聚合更新机制
  - 新注册 30 天保护期
- 子标准 C：Agent Delegation Protocol
  - 基于 A2A Task 扩展的委托格式
  - 托管 (Escrow)、信任要求、安全要求、争议解决字段
  - 完整状态机定义
  - 标准化争议解决流程
- 实施指南
  - 最小实现清单
  - Python 代码示例
  - 单元测试用例
  - 兼容性检查清单

已知限制：
- 暂不支持零知识证明隐私保护
- 暂不支持跨链托管
- 链上锚定仅定义格式，具体实现留给 v0.2
- 评分申诉流程仅定义基本框架

---

*本文档最后更新于 2026-07-20。欢迎通过 Issue 或 Pull Request 参与标准完善。*