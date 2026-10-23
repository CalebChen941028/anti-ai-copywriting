# Contributing to anti-ai-copywriting

[English](#english) | [中文](#中文)

---

## English

Thank you for contributing to `anti-ai-copywriting`!

### Guidelines
1. **Zero External Dependencies**: The core linter in `lint/anti_ai_lint/` must rely strictly on the Python standard library.
2. **Regression Fixtures**: If you propose a new forbidden trope or syntax pattern, include corresponding `.before.md` and `.after.md` pairs under `tests/fixtures/`.
3. **Tests**: All tests must pass:
   ```bash
   python3 -m unittest discover -s tests
   ```

---

## 中文

感谢参与 `anti-ai-copywriting` 项目建设！

### 贡献准则
1. **零第三方依赖**：`lint/anti_ai_lint/` 下的检查器代码必须严格基于 Python 标准库开发。
2. **回归样例**：新增禁用词或句法检测模式时，请在 `tests/fixtures/` 对应场景中补充 `.before.md` 与 `.after.md` 对照样本。
3. **测试通过**：提交前确保所有单测通过：
   ```bash
   python3 -m unittest discover -s tests
   ```
