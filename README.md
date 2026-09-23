# tongue_demo — 舌頭影像即時分析 demo（FastAPI 骨架）

本機夾：`D:\tongue\code\tongue_demo`（2026-09-23 自桌面複製；GitHub `a7266165/tongue_demo`，**公開 repo**）。

## 現況（2026-09-23 盤點）
- 這是 FastAPI 服務骨架：上傳／WebSocket 路由、資料夾監看、pipeline `classify → mask → white_balance`。
- `classify.py` 是 stub（一律回 front）；`models/classify_model.onnx` 本機不存在，分類模型從未整合。
- 週會與 DHA2026 海報展示的是另一套 Flask＋SAM2 系統與 `DeepAVR_dataset_CenterHD` 資料集，**不在本機**（見 `D:\tongue\report\`）。

## 執行
```
conda env create -f environment.yml      # env 名 tongue_env（本機已有）
conda activate tongue_env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
路徑由 `.env` 決定（不入 git；範本 `.env.example`）。本機 `.env` 把 DATA_DIR 指到 `D:\tongue\workspace\demo\`，服務啟動時自建 incoming／processed／results；repo 內不再放 data 夾。

## 公開 repo 注意
`data/`、`.env`、`models/` 已在 `.gitignore`；影像、模型、憑證一律不 commit。
