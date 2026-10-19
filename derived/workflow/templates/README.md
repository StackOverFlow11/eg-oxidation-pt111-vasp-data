# GC-CHE 计算模板矩阵（3 档 × 3 体系类型）

生成日期：2026-10-12。canonical 源：本目录（repo）；部署到 production host ``（含 script.sh）。

## 档位（沿流程从左到右）

| 档 | 目录 | ENCUT | K 点(slab 系) | EDIFF | POTIM | 离子设置 | 用途 |
|---|---|---|---|---|---|---|---|
| 预优化 | `pre_opt/` | 400 | Γ111 | 5E-5 | 0.5 | IBRION=2 NSW=1000 EDIFFG=−0.05 | 出几何 |
| 精细优化 | `fine_opt/` | 500 | 3×3×1 | 1E-5 | 0.1 | IBRION=2 NSW=1000 EDIFFG=−0.01 | 出能量（几何+电荷双收敛） |
| 频率 | `frq/` | 500 | 3×3×1 | 1E-7 | 0.015 | IBRION=5 NFREE=2 | 热校正 |

## 体系类型

| 类型 | ISPIN | ISMEAR/σ | K 点 | LSOL |
|---|---|---|---|---|
| `gas/` | **1** | 0 / 0.05 | Γ111 | ❌ 中性真空 |
| `slab/` | 2 | 1 / 0.2 | 按档位 | ✅ LSOL+ISOL=2+钉扎 |
| `absorbent/` | 2 | 1 / 0.2 | 按档位 | ✅ LSOL+ISOL=2+钉扎 |

## 硬规矩（每条都有事故/文献依据）

1. **恒电势禁止 NSW=0**：钉扎由离子步驱动，NSW=0 静默失效（源码 main.F + 开发者 issue #6 实锤）。fine_opt 用 NSW=1000 真实弛豫，靠 check_EFERMI 双收敛。
2. **气体分子一律 ISPIN=1**：ISPIN=2 会卡三重态（H₂ 实测 +3.24 eV 垃圾能量）。
3. **EFERMI_ref = −4.52 − U_RHE + 0.826**：0.4V→−4.094，0.9V→−4.594（PBE 锚点 −4.52；R_ION 固定 3.0——容量实测 3.9e vs 4.0 的 1.1e；锚点对 R_ION 为二阶小项，SI 声明即可）。
4. **Ω 直接取 E0**：恒电势输出已含 −q_sol·μe，严禁再手工 ±Δn·μe。
5. 验收每个钉扎 job：`grep -c "Adjusting number of electrons" OUTCAR` ≥1 且 |E-fermi − ref| < 0.01 eV 且 q_sol≠0。
6. freq 降本走**偏 Hessian**（只算吸附物+近邻表层，Chen 2020 先例），不是降 K 点（无文献支持）。
7. 脚本不跨集群复用：group 用 `` 模板 script.sh（ppn=24, Intel 2018）。

## 待办

- [x] 偏 Hessian 固定原子流程：`../src/scripts/fix_atoms.py`（即 `GC_CHE/workflow/src/scripts/`；`--mode bottom2` 固定底部两层 / `--mode slab_all` 固定全部 Pt），本地与 group md_env 输出逐位一致 ✓（group 部署于 ``）
- [ ] frq 的恒电势 IBRION=5 尚无应用先例，首批生产前小体系验证（成功即 SI 亮点）
- [ ] c 轴 26.8 Å 真空抽检（Chen 2020 经验 >50 Å；旧数据无饱和警告）
