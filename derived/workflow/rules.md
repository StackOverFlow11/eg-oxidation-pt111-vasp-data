# rules.md — 硬规则与坑（按事故排序）

> 每条规则背后都有旧项目的实际事故或源码级证据。取证细节见 `../../audit/` 各报告。

## 1. 系综规则（账本合法性的根基）

- 同一个态的能量必须整套同系综：恒电势 opt 的能量 + 恒电势 freq 的校正；禁止带电 E0 + 中性 Gcorr 拼接（旧 Re2 表 8 个 G 值全犯了这个）。
- 跨系综（真空 A 类 ↔ 恒电势 B/C 类）能量**不可比**，禁止相减。
- Ω 直接取 E0；严禁再 ±Δn·μe（双重记账）。
- 旧 chem 钉扎数据（BEEF 锚、ENCUT=600）与本流水线（PBE 锚、500）**不可解析换算**，只能重算；构型可作初猜。R_ION 两机已统一 3.0。

## 2. 恒电势 job 验收（每个都要做）

```bash
grep -c "Adjusting number of electrons" OUTCAR   # ≥1，否则钉扎没启动
grep 'E-fermi' OUTCAR | tail -1                  # 与 EFERMI_ref 差 <0.01 eV
grep 'q_sol' OUTCAR | tail -1                    # 非零
```

- NSW=0 时钉扎静默失效（源码 main.F:3711 离子步更新区 + 开发者 issue #6 原话）。
- 真实电子数 = OUTCAR 头部 NELECT + q_sol 终值（头部 NELECT 恒为整数，不能直接判断带电）。
- 验收失败的产物禁止入账（旧 SI −0.09 eV 就是 NSW=0 单点产物混进去的事故）。

## 3. 输入文件规则

- 气体分子 ISPIN=1（ISPIN=2 卡三重态；H₂ 实测 E0=+3.24 eV 的垃圾，正确值 −6.77）。
- POTCAR 元素顺序 = POSCAR 第 6 行顺序；化学系与 group 的 PAW_PBE 库 md5 已验一致。
- 固定原子标志每步用 `fix_atoms.py` 重新生成，不继承上一步的 CONTCAR 标志（虽然本流程两种模式固定集合相同，但重新生成零成本、防漂移）。
- 不要从生产活目录拷模板（会把输出残留带过来）；从 `templates/` 拷。

## 4. 已知风险与待验证项

- frq 默认中性近似（无 LSOL），已按用户 2026-10-12 决定写入模板；恒电势 IBRION=5 作抽检变体（把 LSOL 段加回即可），首批验证其一。
- c 轴 26.8 Å（Chen 2020 经验 Const-U 要 >50 Å）：旧 6 个钉扎 OUTCAR 无饱和警告，实证够用；`_ch2ohcoo+_h/0.4V` 已撞一次（q=1.068/上限 1.16）。**裁定：真空层不加**（全局一致性问题，要加就得全体系加）；撞墙的单态处置 = 先试 500 eV 细网格，再不行该步退中性+声明。SI 补一条真空抽检。
- ZPE 的恒电势/中性差异文献空白：计划对 1–2 个代表态抽检。
- 溶剂下 CI-NEB 无合体 binary：要么重编译（VASPsol++×VTST 叠 patch），要么 CC-NEB+EGC 外推（<20 meV 先例）。

## 5. 历史事故档案（别重蹈）

- `ch2ohcooh/0.4V/2/opt` 错电位（EFERMI_ref=−4.644 混在 0.4V 树）——目录名与电位标记必须一致。
- OER 的 O(hcp) 能量曾串号成 fcc 的值——同名多构型必须带位点标签。
- log.xlsx 手抄能量混 sigma→0 / without-entropy（系统差 ~0.08 eV）——只信程序化提取。
- cineb image00 曾把带电端点 OUTCAR 混入中性 NEB 能带——跨系综拼图是非法的。
- 2026-10-13 新事故：\*OOH 在恒电势+隐式溶剂 pre_opt 中解离（OH 散入溶剂）——该物种两电位作废；以及 ZBRENT bracketing（续跑 CONTCAR→POSCAR 即解）与 CG 极限环（自由原子力 <0.08 放行）两类良性失败模式已归档 start.md。
