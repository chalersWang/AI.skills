# AXI总线测试点Checklist

## 概述

本Checklist提供AXI总线接口验证的完整测试点参考，适用于芯片集成阶段（IT级）的总线接口验证。

## AXI协议版本说明

| 版本 | 说明 | 支持情况 |
|------|------|---------|
| AXI4 | 完整版，支持突发长度1-256 | 必需支持 |
| AXI4-Lite | 简化版，仅支持突发长度1，不支持突发 | 常用 |
| AXI4-Stream | 流式数据传输，无地址通道 | 可选 |

## 信号清单

### 写地址通道 (AW)
| 信号 | 方向 | 说明 |
|------|------|------|
| AWVALID | Master→Slave | 地址有效 |
| AWREADY | Slave→Master | 从机就绪 |
| AWADDR | Master→Slave | 写地址 |
| AWBURST | Master→Slave | 突发类型 (00=FIXED, 01=INCR, 10=WRAP) |
| AWLEN | Master→Slave | 突发长度 (0-255) |
| AWSIZE | Master→Slave | 突发大小 (字节数) |
| AWID | Master→Slave | 事务ID |
| AWPROT | Master→Slave | 保护属性 |
| AWCACHE | Master→Slave | Cache属性 |
| AWQOS | Master→Slave | QoS优先级 |
| AWREGION | Master→Slave | Region标识 |
| AWUSER | Master→Slave | 用户自定义 |

### 写数据通道 (W)
| 信号 | 方向 | 说明 |
|------|------|------|
| WVALID | Master→Slave | 数据有效 |
| WREADY | Slave→Master | 从机就绪 |
| WDATA | Master→Slave | 写数据 |
| WSTRB | Master→Slave | 字节使能 |
| WLAST | Master→Slave | 突发最后数据 |
| WID | Master→Slave | 事务ID |
| WUSER | Master→Slave | 用户自定义 |

### 写响应通道 (B)
| 信号 | 方向 | 说明 |
|------|------|------|
| BVALID | Slave→Master | 响应有效 |
| BREADY | Master→Slave | Master就绪 |
| BRESP | Slave→Master | 响应状态 (00=OK, 01=EXOK, 10=SLVERR, 11=DECERR) |
| BID | Slave→Master | 事务ID |

### 读地址通道 (AR)
| 信号 | 方向 | 说明 |
|------|------|------|
| ARVALID | Master→Slave | 地址有效 |
| ARREADY | Slave→Master | 从机就绪 |
| ARADDR | Master→Slave | 读地址 |
| ARBURST | Master→Slave | 突发类型 |
| ARLEN | Master→Slave | 突发长度 |
| ARSIZE | Master→Slave | 突发大小 |
| ARID | Master→Slave | 事务ID |
| ARPROT | Master→Slave | 保护属性 |
| ARCACHE | Master→Slave | Cache属性 |
| ARQOS | Master→Slave | QoS优先级 |
| ARREGION | Master→Slave | Region标识 |
| ARUSER | Master→Slave | 用户自定义 |

### 读数据通道 (R)
| 信号 | 方向 | 说明 |
|------|------|------|
| RVALID | Slave→Master | 数据有效 |
| RREADY | Master→Slave | Master就绪 |
| RDATA | Slave→Master | 读数据 |
| RRESP | Slave→Master | 响应状态 |
| RID | Slave→Master | 事务ID |
| RLAST | Slave→Master | 突发最后数据 |
| RUSER | Slave→Master | 用户自定义 |

## 测试点分类

### 1. 基本读写测试 (P0)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-BASIC-001 | SINGLE读 (AWLEN=0) | 单次读事务 |
| AXI-BASIC-002 | SINGLE写 (ARLEN=0) | 单次写事务 |
| AXI-BASIC-003 | INCR4读 | 增量突发4次 |
| AXI-BASIC-004 | INCR4写 | 增量突发4次 |
| AXI-BASIC-005 | WRAP4读 | 回环突发4次 |
| AXI-BASIC-006 | WRAP4写 | 回环突发4次 |
| AXI-BASIC-007 | FIXED读 | 固定地址突发 |
| AXI-BASIC-008 | FIXED写 | 固定地址突发 |

### 2. 握手时序测试 (P0)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-HSK-001 | VALID先高 | Master先发地址/数据 |
| AXI-HSK-002 | READY先高 | Slave先就绪等待 |
| AXI-HSK-003 | 同时拉高 | 零等待周期 |
| AXI-HSK-004 | 背靠背传输 | 无空闲周期连续突发 |
| AXI-HSK-005 | 等待周期 | READY保持低插入等待 |
| AXI-HSK-006 | VALID保持 | READY变化时VALID保持 |

### 3. 地址通道测试 (P0-P1)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-ADDR-001 | 4字节对齐 | 地址低2位=00 |
| AXI-ADDR-002 | 8字节对齐 | 地址低3位=000 |
| AXI-ADDR-003 | 非对齐起始 | 起始地址非对齐 |
| AXI-ADDR-004 | 4KB边界 | 跨越4KB边界 |
| AXI-ADDR-005 | 最大地址边界 | 地址极值测试 |
| AXI-ADDR-006 | 突发边界 | 突发长度恰好到边界 |

### 4. 数据通道测试 (P0)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-DATA-001 | 全字节使能 | WSTRB=4'hF |
| AXI-DATA-002 | 半使能 | WSTRB混合 |
| AXI-DATA-003 | 单字节使能 | WSTRB=4'h1/2/4/8 |
| AXI-DATA-004 | WLAST正确 | 突发最后数据WLAST=1 |
| AXI-DATA-005 | 窄传输 | 突发宽度<数据宽度 |
| AXI-DATA-006 | 数据一致性 | 读返回=写数据 |

### 5. 突发长度测试 (P0-P1)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-LEN-001 | 长度1 | SINGLE传输 |
| AXI-LEN-002 | 长度4 | 短突发 |
| AXI-LEN-003 | 长度8 | 中等突发 |
| AXI-LEN-004 | 长度16 | 最大常见突发 |
| AXI-LEN-005 | 长度255 | AXI4最大长度 |

### 6. 突发大小测试 (P1)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-SIZE-001 | 1字节 | SIZE=0 |
| AXI-SIZE-002 | 2字节 | SIZE=1 |
| AXI-SIZE-003 | 4字节 | SIZE=2 |
| AXI-SIZE-004 | 8字节 | SIZE=3 |
| AXI-SIZE-005 | 16字节 | SIZE=4 |

### 7. 错误响应测试 (P1)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-ERR-001 | SLVERR读 | 从机返回错误 |
| AXI-ERR-002 | SLVERR写 | 写错误响应 |
| AXI-ERR-003 | DECERR | 无效地址访问 |
| AXI-ERR-004 | 错误不阻塞 | 错误后正常事务继续 |

### 8. 原子操作测试 (P1)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-ATOM-001 | 独占读 | EXCLUSIVE读获取锁 |
| AXI-ATOM-002 | 独占写成功 | 独占写后无破坏写成功 |
| AXI-ATOM-003 | 独占写失败 | 中间被破坏写失败 |
| AXI-ATOM-004 | 独占失败恢复 | 失败后可继续正常访问 |

### 9. ID和顺序测试 (P1-P2)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-ID-001 | 相同ID顺序 | 相同ID按顺序完成 |
| AXI-ID-002 | 不同ID乱序 | 不同ID可乱序 |
| AXI-ID-003 | ID匹配 | 写响应BID=AWID |
| AXI-ID-004 | ID匹配 | 读响应RID=ARID |

### 10. 协议特性测试 (P2)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-PROTO-001 | PROT信号 | 安全等级验证 |
| AXI-PROTO-002 | CACHE信号 | Cacheable属性 |
| AXI-PROTO-003 | QOS信号 | 优先级处理 |
| AXI-PROTO-004 | REGION信号 | Region合法性 |
| AXI-PROTO-005 | USER信号 | 用户自定义传递 |

### 11. 时序边界测试 (P1)

| 测试点ID | 测试内容 | 验证目标 |
|---------|---------|---------|
| AXI-TIMING-001 | RVALID保持 | READY为低时数据保持 |
| AXI-TIMING-002 | 通道依赖 | AW不能晚于W |
| AXI-TIMING-003 | 最大等待 | 长时间等待恢复 |
| AXI-TIMING-004 | 最小间隔 | 事务最小间隔 |

## 优先级说明

| 优先级 | 说明 | 必须测试 |
|--------|------|---------|
| P0 | 核心功能 | 是 |
| P1 | 重要功能 | 建议 |
| P2 | 扩展功能 | 可选 |

## 常见错误场景

### 1. 协议违规
- VALID拉高后不能立即拉低直到握手成功
- WLAST必须仅在突发最后一次拉高
- 地址必须在数据前到达

### 2. 边界条件
- 4KB边界跨越（地址计算错误）
- 突发长度与大小组合（对齐计算）
- 非对齐起始地址

### 3. 错误处理
- 无效地址访问
- 从机超时
- 总线错误