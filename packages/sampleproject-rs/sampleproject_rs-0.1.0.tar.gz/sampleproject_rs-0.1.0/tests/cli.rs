use assert_cmd::Command;

#[test]
fn test_cli() {
    let mut cmd = Command::cargo_bin("sample").unwrap();
    let assert = cmd.assert();
    assert.success().stdout("Call your main application code here\n");
}
