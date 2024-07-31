# evidenceFinder

Find evidence and check accuracy of text information using Google Search.

# 環境構築

- perplexityAIのコレクション
https://www.perplexity.ai/collections/240718-evidencefinder-hT9oOlr0TIqGwOR4SoAFkQ

- pythonをインストールしておく
    - Mac版：https://qiita.com/omo_taku/items/bc97f69391b2f4627f36
    - Windows版：https://www.python.jp/install/windows/install.html

## 仮想環境の使い分け
- venvを利用
- 絶対正攻法じゃない気がするけど、
    - mac用："mac_venv"フォルダ
    - windows用："win_venv"フォルダ
    のように仮想環境を切り替えて開発したい。

### Macの場合
```
# mac用仮想環境に入る
source mac_venv/bin/activate
### (mac_venv)$ となれば成功。

# 必要パッケージの一括読み込み
pip install -r requirements.txt

# 新規ライブラリ(パッケージ)のinstall
pip install (インストールしたいパッケージ名)

# requirements.txtの上書き方法
pip freeze > requirements.txt
```


### Windowsの場合
- pipコマンドがバグるときは "python -m" を冒頭につけると動きそう(適当)

```
# windows版仮想環境に入る
###VScodeのターミナルで下記を入力
.\\win_venv\Scripts\activate  

# 必要パッケージの一括読み込み
python -m pip install -r requirements.txt

# 新規ライブラリ(パッケージ)のinstall
python -m pip install (インストールしたいパッケージ名)

# requirements.txtの上書き方法
python -m pip freeze > requirements.txt
```
