# conventions.md — 热力学约定（冻结版）

> 本文件是 GC-CHE 记账的唯一 SoT。改约定必须改这里并同步 `templates/`。推导与文献出处：`../../literature/notes/GC_CHE_methodology_summary.md`。

## 锚点

$$E_{F,\mathrm{ref}} = \varepsilon_{F,\mathrm{SHE}} - U_{\mathrm{SHE}} = -4.52 - U_{\mathrm{RHE}} + 0.826$$

- 0.4 V → $E_{F,\mathrm{ref}} = -4.094$ eV
- 0.9 V → $E_{F,\mathrm{ref}} = -4.594$ eV
- −4.52 eV = PBE 的 $\varepsilon_{F,\mathrm{SHE}}$（VASPsol++ 官方数值谱系）
- 0.826 = 0.059×14（实验 1M KOH，pH≈14，RHE→SHE 折算）
- 绑定条件：PBE+D3、R_ION=3.0（容量约束，2026-10-13 实测）、C_MOLAR=1.0、ISOL=2；换泛函则锚点需重校准（Islam 2023 §IV.5）

## 巨势与自由能

$$\Omega = A - q_{\mathrm{sol}}\,\mu_e$$

- VASPsol++ 恒电势输出的 E0 已是 $\Omega$，态间直接相减
- 严禁再手工 $\pm\,\Delta n\cdot\mu_e$（双重记账）

$$G_\varphi(\text{电极态}) = \Omega + G_{\mathrm{corr}}(\text{freq})$$

- $T = 300.15$ K；$G_{\mathrm{corr}}$ 取 vaspkit 输出的 `Thermal correction to G(T)` 整值，不手拼

## 台阶图

$$\Delta G_\varphi = \sum \Omega_\varphi(\text{电极态}) \pm \sum G^{\circ}(\text{中性分子}) - \tfrac{1}{2}\mu^{\circ}(\mathrm{H_2})\cdot\Delta n_{\mathrm{H}} + e\varphi\cdot n_e$$

- 中性气相分子：$\Omega = G$，不带 $\mu_e$ 项
- $(\mathrm{H^+}+e^-)$ 仍用 $\tfrac12\mathrm{H_2}$ 替代
- G(O₂) 沿用实验替代：$2G(\mathrm{H_2O}) - 2G(\mathrm{H_2}) + 4.92$ eV
- 压力：EG / H₂ = 1 bar（0.986923 atm），H₂O = 0.035 bar（0.034542 atm）

## 验收自检

$U\to0$ 时整电子转移极限必须退化回经典 CHE 台阶图（Hörmann 2024 严格证明）。

## 精度档位（收敛测试依据：../../audit/conv_test_plan.md）

| 档 | ENCUT | K 点(slab 系) | EDIFF | POTIM | 离子设置 |
|---|---|---|---|---|---|
| pre_opt | 400 | Γ111 | 5E-5 | 0.5 | IBRION=2 NSW=1000 EDIFFG=−0.05 |
| fine_opt | 500 | 3×3×1 | 1E-5 | 0.1 | IBRION=2 NSW=1000 EDIFFG=−0.01 |
| frq | 500 | 3×3×1 | 1E-7 | 0.015 | IBRION=5 NFREE=2 |

gas 类全程 Γ111、ISPIN=1、无 LSOL；slab/absorbent 类 ISPIN=2、LSOL 钉扎。
