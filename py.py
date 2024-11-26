import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
from tf.app import use
from collections import defaultdict, Counter
import re
from community import community_louvain

# 日本語フォント対応
plt.rcParams['font.family'] = 'Meiryo'

# ETCBC/bhsaデータセットをロード
A = use('ETCBC/bhsa', hoist=globals())

# 「Samuel I」の書から人物（名詞）を抽出
query = """
book book=Samuel_I
  chapter chapter=13
    clause
      word sp=nmpr
"""

results = A.search(query)

# 結果を30個に制限
results = results[:30]

# 結果の表示
print(f"結果数: {len(results)}")
A.table(results[:10])

# 人物ごとに出現した節を格納する辞書
person_to_verses = defaultdict(list)

# 検索結果を処理
for result in results:
    person = result[2]  # word ID
    verse = result[0]  # verse ID
    person_to_verses[person].append(verse)

# 人物IDを名前に変換する関数
def get_person_name(person_id):
    info = A.pretty(person_id)
    if info is not None:
        name_match = re.search(r"\b([A-Za-z]+)\b", info)
        if name_match:
            return name_match.group(1)
        else:
            return f"Unknown_{person_id}"
    else:
        return f"Unknown_{person_id}"

# 同じ節に登場する人物同士の関係性を作成
edge_weights = Counter()
for verses in person_to_verses.values():
    for verse in set(verses):  # 重複を排除
        persons = [get_person_name(person) for person, v in person_to_verses.items() if verse in v]
        for person1, person2 in combinations(persons, 2):
            edge_weights[(person1, person2)] += 1

# 最大30エッジに制限
top_edges = edge_weights.most_common(30)
print(f"Top 30 edges: {top_edges}")  # 確認用

# NetworkXでグラフを作成
G = nx.Graph()

# 制限したエッジと重みを追加
for (person1, person2), weight in top_edges:
    G.add_edge(person1, person2, weight=weight)

# コミュニティ検出
partition = community_louvain.best_partition(G)

# ノードの色をコミュニティに基づいて決定
node_colors = [partition[node] for node in G.nodes()]

# ノードの出現回数（重要度に応じてサイズ変更）
node_sizes = {person: len(verses) for person, verses in person_to_verses.items()}
sizes = [node_sizes.get(node, 1) * 200 for node in G.nodes()]

# グラフを可視化
fig, ax = plt.subplots(figsize=(14, 12))  # axを定義

# グラフのレイアウトを設定
pos = nx.spring_layout(G, seed=42)

# グラフを描画
nx.draw(G, pos, node_size=sizes, node_color=node_colors, with_labels=True, cmap=plt.cm.rainbow, font_weight='bold', ax=ax)

# カラーバーを追加
sm = plt.cm.ScalarMappable(cmap=plt.cm.rainbow, norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
sm.set_array(node_colors)  # node_colorsをセット
plt.colorbar(sm, ax=ax, label="コミュニティ")  # axを指定

# タイトルを追加
plt.title("Samuel I - 人物間のネットワークとコミュニティ", fontsize=16)

# グラフを表示
plt.show()













