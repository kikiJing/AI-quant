# Git 推送失败 - 解决方案

## 问题描述
推送至GitHub失败，错误信息：
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

## 原因
SSH密钥未配置或未添加到GitHub账号。

## 解决方案

### 方案1：配置SSH密钥（推荐）

1. **生成SSH密钥**（如果还没有）：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
按3次回车（使用默认路径，不设置密码）

2. **查看公钥**：
```bash
cat ~/.ssh/id_ed25519.pub
```

3. **复制公钥内容**，然后：
   - 访问 https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容
   - 保存

4. **测试连接**：
```bash
ssh -T git@github.com
```

5. **重新推送**：
```bash
cd "/Users/kikijing/Desktop/AI quant"
git push origin main
```

### 方案2：使用HTTPS方式（临时方案）

1. **修改远程仓库URL**：
```bash
cd "/Users/kikijing/Desktop/AI quant"
git remote set-url origin https://github.com/kikiJing/AI-quant.git
```

2. **推送**（会要求输入GitHub用户名和密码）：
```bash
git push origin main
```

注意：GitHub已不支持密码推送，需要使用Personal Access Token。
- 创建Token：https://github.com/settings/tokens
- 推送时使用Token作为密码

### 方案3：手动推送（让用户自己操作）

文件已提交到本地Git仓库，位于：
- 分支：main
- 最新提交：6a69b7d

您可以在配置好SSH密钥后，手动运行：
```bash
cd "/Users/kikijing/Desktop/AI quant"
git push origin main
```

## 当前状态

✅ 所有文件已成功提交到本地Git仓库
✅ ai-quant-lab文件夹包含所有必要文件：
   - 数据 (data/)
   - 脚本 (scripts/)
   - 文档 (docs/)
   - Jupyter Notebook (notebooks/)
   - 配置文件 (requirements.txt, .gitignore, README.md)

⏳ 需要推送到GitHub远程仓库

## 已提交的文件列表

```
ai-quant-lab/.gitignore
ai-quant-lab/README.md
ai-quant-lab/config_example.py
ai-quant-lab/data/byd_002594_daily.csv
ai-quant-lab/data/moutai_600519_daily.csv
ai-quant-lab/data/ningde_times_300750_daily.csv
ai-quant-lab/data/petro_china_601857_daily.csv
ai-quant-lab/data/ping_an_601318_daily.csv
ai-quant-lab/data/smic_688981_daily.csv
ai-quant-lab/docs/DESIGN_DOCUMENT.md
ai-quant-lab/docs/README_adjustment.md
ai-quant-lab/docs/interface_prototype.html
ai-quant-lab/notebooks/technical_indicators_demo.ipynb
ai-quant-lab/requirements.txt
ai-quant-lab/scripts/apply_adjustment.py
ai-quant-lab/scripts/diagnose_and_adjust_stocks.py
ai-quant-lab/scripts/fetch_adj_factors.py
ai-quant-lab/scripts/fetch_stocks.py
```

## 下一步

请选择上述方案之一配置SSH密钥，然后推送代码到GitHub。
