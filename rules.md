# Rules · 规则

这份文件规定 collection 收什么、怎么记录、怎么增删。网站（Cargo 页面和地图）都以 `_cases/` 里的 md 文件为准。

## 1. 这个 collection 是什么

A collection of good transitional spaces（threshold sequences）in religious buildings, starting from the chapels of the Cambridge colleges.
目的：从好的过渡空间里，读出对比强度（Δ between consecutive segments）和对比持续时间（length of the preceding enclosed segment）。

## 2. 范围（分层，先做第 1 层）

| layer | 范围 | 状态 |
|---|---|---|
| `college-chapel` | 剑桥 31 个学院中有礼拜堂的 23 个 | 进行中 |
| `cambridge-other` | 剑桥市内其他宗教建筑：大学教堂、神学院礼拜堂、Leper Chapel、Cambridge Central Mosque 等 | 待做 |
| `cambridgeshire` | Cambridgeshire 的宗教建筑，如 Ely | 待做 |

## 3. 筛选流程（第 2、3 层使用）

1. **检索范围**：OpenStreetMap 中 `amenity=place_of_worship` 的全部条目（按层的行政边界）。
2. **自动筛选**：按 Historic England 登录等级、建成年代等可自动判断的条件。
3. **人工筛选**：按第 4 节的标准逐条判断，排除的条目记下理由。
4. **检验**：已知的好案例如果没有通过，回头检查标准本身。

每一层都记录每一步的数量（类似 PRISMA 流程图）。

## 4. 收录标准

**意义层面**（满足其一）：
- A. 建筑本身有 threshold 的概念；
- B. 建筑师或文献明确提到这段过渡；
- C. 文化上有 threshold 意义。

**物理层面**（都要满足）：
- 有清楚的 O-C-O 或 C-O-C 序列；
- 至少一个 feature 在相邻路段之间有明显的 Δ，并且有资料可以支持。

**分档**（`tier`）：
- `A`：中间有 threshold，并且有平行的侧边路线；
- `B`：两者有其一；
- `C`：都没有，或待查。

## 5. 记录单位

一个 md 文件 = 一座建筑。一座建筑里可以有多条序列（`sequences`），每条序列由若干路段（`segments`）组成。
> 待定：collection 的单位最终用“建筑”还是“序列”。现在的字段两种都支持。

## 6. 编号

| layer | 前缀 | 例 |
|---|---|---|
| `college-chapel` | C | C01 |
| `cambridge-other` | K | K01 |
| `cambridgeshire` | E | E01 |

编号一经分配不再改；条目被排除时，`status` 改为 `excluded`，不删文件。

## 7. tag 词表

只用下面的词，新增要先写进这里。名称来自资料原文（RCHME、listing、学院资料）。

- 层：`college-chapel` `cambridge-other` `cambridgeshire`
- 状态：`candidate` `shortlist` `excluded`
- threshold 形式：`screen`（木或金属屏风）· `arch`（墙上的拱或门洞）· `vestibule`（屏风之间的小前厅）· `octagonal-ante-chapel` · `crossing`（塔楼下的交叉）· `ascent`（垂直上升）· `side-route`（平行的侧边路线）

## 8. 字段

见 `_cases/C01-kings-college-chapel.md`。必填：`code` `name_en` `name_zh` `layer` `status` `tier` `tags` `lat` `lon` `coord_source` `sources`。

- 坐标用 OpenStreetMap（`osm` 填 OSM 对象，如 `way/123456`）；暂用其他来源时，在 `coord_source` 里写明。
- 尺寸写原文单位，同时给出米（1 ft = 0.3048 m）。
- 建造年代写在 `built`。**不要用 `date` 这个字段名**：GitHub Pages 会把它当成发布日期，写成年代范围会导致网站构建失败。
- **不写个人邮箱**：仓库是公开的，联系方式只放学院官网链接。

## 9. 图和来源

- 每张图都要有：作者、年份、来源链接、许可证。没有许可信息的图不上网站。
- Wikimedia Commons 的图按其许可证（如 CC BY-SA 4.0）署名。
- RCHME（1959）图版：BHO 的再使用条款待核实，核实前只链接、不放图。
- 自己拍的照片和 sketch：标“© Haining Ding”。
- 图例（绘图规则）：粗实线 = 剖到的墙；细实线 = 看到的边；点划线 = 路线；T1、T2… = threshold 位置。

## 10. 怎样增删

- **增加**：复制一个 `_cases/` 文件，改名为 `编号-名称.md`，填好字段，提交。地图会自动加上这个点。
- **排除**：把 `status` 改成 `excluded`，在正文写理由。地图默认不显示 `excluded`。
- **改规则**：改这份文件，并在下面的“修改记录”里写一行。

## 修改记录

- 2026-10-25：第一版。
- 2026-10-25：年代字段由 `date` 改为 `built`。
