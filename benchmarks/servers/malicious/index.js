// 恶意基准样本（用于验证检测器，不要在生产中使用）：
// 1) 硬编码私钥 2) 命令执行 3) 用户输入直达 shell
const os = require('os');
const { exec } = require('child_process');

const privateKey = "-----BEGIN RSA PRIVATE KEY-----\nMIIabcDEFGH\n-----END RSA PRIVATE KEY-----";

data = process.argv[2];
exec("echo " + data);   // 用户输入直达命令执行（taint_flow：data 是污染变量）
os.system("rm -rf /");             // 危险系统调用

module.exports = { privateKey };
