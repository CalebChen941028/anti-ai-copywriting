# Contributing to anti-ai-copywriting

[English](#english) | [中文](#中文)

---

## English

Thank you for contributing to `anti-ai-copywriting`!

### Guidelines
1. **Zero External Dependencies**: The core linter in `lint/anti_ai_lint/` must rely strictly on the Python standard library.
2. **Regression Fixtures**: If you propose a new forbidden trope or syntax pattern, include corresponding `.before.md` and `.after.md` pairs under `tests/fixtures/`.
3. **Open Source Compliance**:
   - Ensure all source files include SPDX license headers (`SPDX-License-Identifier: MIT`).
   - Do not commit proprietary code, credentials, API keys, or temporary files.
   - Respect trademarks: do not claim endorsement or official affiliation with third-party platforms or models (Anthropic, OpenAI, DeepSeek, Google, etc.).
   - Properly attribute inspirations and references (ASD-STE100, Google Research Harness²).
4. **Tests**: All tests must pass:
   ```bash
   python3 -m unittest discover -s tests
   ```

---

## 中文

感谢参与 `anti-ai-copywriting` 项目建设！

### 贡献准则
1. **零第三方依赖**：`lint/anti_ai_lint/` 下的检查器代码必须严格基于 Python 标准库开发。
2. **回归样例**：新增禁用词或句法检测模式时，请在 `tests/fixtures/` 对应场景中补充 `.before.md` 与 `.after.md` 对照样本。
3. **开源合规要求**：
   - 所有源文件需包含 SPDX 许可证标识（`SPDX-License-Identifier: MIT`）。
   - 严禁提交商业保密代码、凭证、密钥或临时生成文件。
   - 尊重知识产权与第三方商标：切勿在文档或代码中声称代表第三方（Anthropic、OpenAI、DeepSeek、Google 等）官方立场。
   - 规范引用理论启发与技术来源（ASD-STE100、Google Research Harness²）。
4. **测试通过**：提交前确保所有单测通过：
   ```bash
   python3 -m unittest discover -s tests
   ```
