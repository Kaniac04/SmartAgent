[English](README.md) | [日本語]

# SmartAgent - AI搭載ドキュメントチャットシステム

SmartAgentは、静的なドキュメントを対話型のチャット体験に変換するモダンなウェブアプリケーションです。検索拡張生成（RAG）を活用することで、ユーザーは自然言語を使用してドキュメントに質問することができます。

---

## 機能

- スマートなウェブスクレイピング: ドキュメントサイトからコンテンツを自動的に抽出・クリーンアップします。
- RAGアーキテクチャ: 高速なセマンティック検索のためにQdrantベクトルデータベースを使用します。
- AIチャット: Mistral AIを搭載した自然言語による対話。
- URLセーフティ: Google Safe Browsing APIを統合し、悪意のあるリンクから保護します。
- リアルタイム追跡: ドキュメントのインデックス作成中の進捗をライブで更新します。
- モダンなUI: ネオンアクセントとレスポンシブデザインを備えた洗練されたダークテーマ。

---

## 技術スタック

- バックエンド: FastAPI (Python 3.9+)
- ベクトルストア: Qdrant
- データベース: MongoDB (セッションおよびメタデータ管理)
- 埋め込みモデル: Sentence Transformers
- LLM: Mistral AI
- セキュリティ: Google Safe Browsing API

---

## 動作原理

1. 取り込み: ユーザーがドキュメントのURLを提供します。
2. スクレイピング: システムがサイトをクロールし、意味のあるテキストを抽出します。
3. インデックス作成: コンテンツをチャンクに分割し、埋め込みに変換してQdrantに保存します。
4. 検索: 質問が行われると、システムはベクトルストアから関連するコンテキストを見つけます。
5. 生成: Mistral AIが、取得したコンテキストに基づいて正確な回答を生成します。

---

## インストール

### 前提条件
- Python 3.9以上
- 稼働中のMongoDBインスタンス
- Qdrantインスタンス

### セットアップ

1. リポジトリをクローンする:
   ```bash
   git clone https://github.com/yourusername/SmartAgent.git
   cd SmartAgent
   ```

2. 仮想環境を作成する:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
   ```

3. 依存関係をインストールする:
   ```bash
   pip install -r requirements.txt
   ```

4. 環境変数:
   ルートディレクトリに .env ファイルを作成します:
   ```env
   MONGODB_URI=your_mongodb_uri
   GOOGLE_SAFE_BROWSING_API_KEY=your_api_key
   QDRANT_HOST=your_qdrant_host
   QDRANT_PORT=6333
   MISTRAL_API_KEY=your_mistralai_api_key
   ```

---

## 使用方法

1. サーバーを起動する:
   ```bash
   python main_.py
   ```

2. ウェブUIにアクセスする:
   ブラウザで http://localhost:8000 を開きます。

---

## プロジェクト構造

```text
SmartAgent/
├── api/                # APIエンドポイント (チャット & スクレイパー)
├── services/           # ビジネスロジック (RAG, スクレイピング, ユーティリティ)
├── static/             # CSS & JSアセット
├── templates/          # HTMLテンプレート (Jinja2)
└── main_.py            # アプリケーションのエントリーポイント
```

---

## ライセンス

MITライセンスの下で配布されています。詳細は LICENSE を参照してください。

---

免責事項: このツールは教育目的で作成されています。ウェブサイトからドキュメントをスクレイピングする際は、必ず許可を得ていることを確認してください。