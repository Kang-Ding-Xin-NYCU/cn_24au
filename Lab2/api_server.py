from flask import Flask, request, jsonify
import networkx as nx

app = Flask(__name__)

graph = nx.Graph()

edges = [
    ('h1', 's1'), ('h2', 's3'), ('h3', 's7'), ('h4', 's5'), ('h5', 's5'),
    ('h6', 's8'), ('h7', 's8'), ('h8', 's6'), ('h9', 's4'),
    ('s1', 's2'), ('s1', 's3'), ('s1', 's6'), ('s2', 's3'), ('s2', 's4'), ('s2', 's5') , ('s2', 's7'),
    ('s3', 's4'), ('s4', 's5'), ('s4', 's8'), ('s5', 's7'), ('s5', 's8'), ('s6', 's7')
]

graph.add_weighted_edges_from((u, v, 1) for u, v in edges)

computed_paths = {}

@app.route('/paths', methods=['POST'])
def calculate_paths():

    data = request.json
    source = data.get('source')
    destination = data.get('destination')

    try:
        graph_temp = graph.copy()
        path1 = nx.shortest_path(graph_temp, source=source, target=destination, weight='weight')

        for u, v in zip(path1[:-1], path1[1:]):
            graph_temp[u][v]['weight'] += 100

        path2 = nx.shortest_path(graph_temp, source=source, target=destination, weight='weight')

        return jsonify({"path1": path1, "path2": path2}), 200
    except nx.NetworkXNoPath:
        return jsonify({"error": "No path found between source and destination"}), 404

@app.route('/paths', methods=['GET'])
def get_all_paths():

    paths_list = [
        {"source": src, "destination": dst, "path1": paths["path1"], "path2": paths["path2"]}
        for (src, dst), paths in computed_paths.items()
    ]
    return jsonify(paths_list), 200

@app.route('/deploy', methods=['POST'])
def deploy_path():

    data = request.json
    switch_id = data.get("switch_id")
    path = data.get("path")

    if not switch_id or not path:
        return jsonify({"error": "Switch ID and path must be provided"}), 400

    return jsonify({"message": f"Path {path} successfully deployed to switch {switch_id}"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
