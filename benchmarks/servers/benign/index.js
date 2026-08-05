// 良性基准样本：仅做本地只读文件读取，无命令执行、无硬编码密钥、无外联。
const fs = require('fs');

function readConfig(path) {
  // 只读、参数化，无 shell 拼接
  return fs.readFileSync(path, 'utf8');
}

module.exports = { readConfig };
