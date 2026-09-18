# DV Skills - 资深芯片验证工程师技能库

本仓库是资深芯片验证工程师的经验沉淀库，聚焦核心验证技术。

## 核心能力

### 1. 边界值分析（Boundary Value Analysis）
**验证工程师最该掌握的基本功**

- 物理边界：硬件设计的物理限制
- 协议边界：接口协议的时序限制
- 配置边界：寄存器可配置范围
- 数据边界：数据有效范围

### 2. VIP使用（Verification IP）

- 快速构建协议合规性测试
- 标准接口（AXI/DDR/USB/PCIe）验证
- VIP与DUT的桥接验证

### 3. AMBA协议验证

- APB/AHB/AXI协议验证
- 突发传输、Outstanding、原子操作
- 协议一致性检查

### 4. DDR/存储接口验证

- DDR初始化与命令序列
- Bank管理、刷新、时序
- 功耗状态切换

### 5. 低功耗验证

- 功耗状态机（PSM）
- Isolation/Retention
- DVFS、Power Gating

## 仓库结构

```
dv_skills/
├── SKILL.md                              # 主技能定义
├── README.md                             # 本文档
├── dv_skills.skill                       # 打包技能文件
│
├── references/
│   ├── boundary_value_analysis.md         # 边界值分析详解
│   ├── coverage_model_design.md          # 覆盖模型设计
│   ├── verification_methodology.md        # 验证方法论
│   ├── vip_usage.md                      # VIP使用指南 [新增]
│   ├── amba_verification.md              # AMBA协议验证 [新增]
│   ├── ddr_verification.md               # DDR验证指南 [新增]
│   └── low_power_verification.md         # 低功耗验证 [新增]
│   └── uvm_verification.md               # UVM验证实战 [新增]
│
└── test/
    ├── bva_examples.md                    # 边界值分析示例
    ├── vip_test_examples.md              # VIP测试示例 [新增]
    └── amba_test_examples.md             # AMBA测试示例 [新增]
```

## 使用方法## 使用方法

### 在OpenClaw中加载本技能
将本仓库克隆到你的skills目录后，可以通过以下方式触发：
- 询问边界值分析相关问题
- 需要VIP使用建议
- AMBA/DDR协议验证咨询
- 低功耗验证方案设计

### 本地查阅
```bash
# 克隆仓库
git clone https://gitcode.com/MrYellowBread/dv_skills.git

# 查看边界值分析参考
cat references/boundary_value_analysis.md

# 查看VIP使用指南
cat references/vip_usage.md
```

## 知识积累

本仓库持续更新，欢迎提交PR分享你的验证经验和技巧。

### 贡献指南
1. 在references目录添加新的主题文档
2. 在test目录添加示例和测试点
3. 更新SKILL.md中的引用
4. 使用skill-creator重新打包

## 关联仓库

- [chip-verif-reviewer](https://gitcode.com/MrYellowBread/dv_reviewer) - 芯片验证测试点评审工具

---
*持续学习，持续验证，做靠谱的芯片*

## 测试

dv_skills 使用自动化测试框架验证技能库质量。

详见 [test_env/README.md](test_env/README.md)。
