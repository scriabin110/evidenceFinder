# evidenceFinder
Find evidence and check accuracy of text information using Google Search.


## 環境構築




============================================================

This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## 環境構築

- node と yarn のインストール

```
# brew経由でnodeのインストール
# もしbrew入ってなかったら、https://brew.sh/index_ja.html
brew install node


# パスを通す
export PATH=/usr/local/opt/node/bin:$PATH

# bash_profileのリロード
source ~/.bash_profile

# nodeの確認
# v18.19.0と表示されればOK
node -v

# yarnのインストール
npm install -g yarn

# yarnがインストールできているか確認
yarn -v

```

- 必要なモジュールのインストール

```
yarn
```

## 起動方法

```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## branch の管理について

- git-flows に準拠している
  https://cloudsmith.co.jp/blog/efficient/2020/08/1534208.html#:~:text=git%2Dflow%E3%81%A8%E3%81%AFGit,%E3%81%99%E3%82%8B%E3%81%93%E3%81%A8%E3%82%92%E9%98%B2%E3%81%8E%E3%81%BE%E3%81%99%E3%80%82

- 開発する時のお左方

1. develop に移動する
1. git pull する
1. feature/xxxx のブランチ作成
1. 作業
1. add と commit を繰り返す
1. git push する
1. github 上で、pull request を作る
1. slack などでメンションする

# Backend

## DB postgresDB

BaaS supabase: https://supabase.com/dashboard/project/ztixddvpmmrdzsngtgfq/database/tables

## migrate: prisma

- チートシート
  https://qiita.com/ryskBonn92/items/c45e22ce5f37d82ec8de

- db 初期設定

```
$npx prisma migrate dev --name init
```

-
-
