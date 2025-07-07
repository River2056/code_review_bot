# Code Review 機器人

## 工具介紹
工具目前只支援使用本機`Ollama`去做code review (為了不讓code外洩), 使用前請先確保機器已安裝`Ollama`.
執行程式之後, 會將diff的內容餵給AI讓他code review, 並且不會馬上結束, 會進入QA環節 (questions to ask (type q to quit):)
可以持續跟AI對話. 按q結束會將剛剛的內容輸出成log檔

### 安裝說明
- 本機裝`Ollama`
- 下載模型, 筆電建議使用`qwen2.5-coder`, 一般都用7b版本
- 安裝 <a href="https://docs.astral.sh/uv/" target="_blank">`uv`</a>
    - mac 有使用 homebrew 的同學: `brew install uv`
- `config.toml` 將對應的 `repo-location` 改成自己的 repository 路徑
    - `language` 此參數為告訴 AI 你的 code 是哪種語言
    - `model` 可以根據自己的喜好替換成別的模型, 前提是要先下載好
    - `review-branch` 代表你的功能 feature branch
    - `dest-branch` 代表要 merge 進去的目標 branch
    - `output-dir` AI 分析完程式不會立即結束, 按 q 結束程式會將剛剛的對話紀錄下來並輸出至這個目錄底下
- 執行程式之前先跑一下 `uv sync` 將相關 dependency 抓下來
- 執行`uv run main.py` (有用Justfile的同學可以直接`just`)
