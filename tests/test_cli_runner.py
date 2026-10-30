from test_bot import format_terminal_box, parse_cli_args


def test_parse_cli_args_defaults():
    args = parse_cli_args([])
    assert args.query == "How do I add a YouTube video?"
    assert args.top_k == 3
    assert args.verbose is False
    assert args.interactive is False


def test_parse_cli_args_custom():
    args = parse_cli_args(["--query", "Custom Query", "--top-k", "5", "--verbose", "-i"])
    assert args.query == "Custom Query"
    assert args.top_k == 5
    assert args.verbose is True
    assert args.interactive is True


def test_format_terminal_box_structure():
    title = "TEST HEADER"
    body = "Line 1\nLine 2"
    box = format_terminal_box(title, body, width=60)
    assert "+---" in box
    assert "TEST HEADER" in box
    assert "Line 1" in box
    assert "Line 2" in box
    lines = box.strip().splitlines()
    assert lines[0].startswith("+")
    assert lines[-1].startswith("+")
