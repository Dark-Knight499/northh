import pytest


class TestAIModuleImport:
    def test_module_importable(self):
        import src.functions.ai as ai

        assert ai is not None

    def test_rewrite_stub_exists(self):
        from src.functions.ai import rerewrite_with_ai

        assert callable(rerewrite_with_ai)

    def test_generate_content_returns_placeholder(self, tmp_path):
        from src.functions.ai import generate_content_with_ai

        result = generate_content_with_ai("original content", "test context")
        assert isinstance(result, str)
        assert len(result) > 0


class TestRerewriteStub:
    def test_creates_ai_file(self, tmp_path):
        from src.functions.ai import rerewrite_with_ai

        original = tmp_path / "test.md"
        original.write_text("hello")
        rerewrite_with_ai(str(original), "gpt-4")
        ai_file = tmp_path / "test_ai.md"
        assert ai_file.is_file()

    def test_ai_file_has_content(self, tmp_path):
        from src.functions.ai import rerewrite_with_ai

        original = tmp_path / "test.md"
        original.write_text("hello")
        rerewrite_with_ai(str(original), "gpt-4")
        content = (tmp_path / "test_ai.md").read_text()
        assert len(content) > 0
