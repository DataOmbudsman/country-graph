function drawGraph(graph) {

    var svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter()
        .append("circle")
        .attr("r", 5);

    var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter()
        .append("line");

    var linkForce = d3.forceLink(graph.links)
        .id(function (d) { return d.name; })

    var simulation = d3.forceSimulation()
        .nodes(graph.nodes)
        .force("charge_force", d3.forceManyBody().strength(-15))
        .force("center_force", d3.forceCenter(width / 2, height / 2))
        .force("links", linkForce);

    function tickActions() {
        node
            .attr("cx", function (d) { return d.x; })
            .attr("cy", function (d) { return d.y; });

        link
            .attr("x1", function (d) { return d.source.x; })
            .attr("y1", function (d) { return d.source.y; })
            .attr("x2", function (d) { return d.target.x; })
            .attr("y2", function (d) { return d.target.y; });
    }

    simulation.on("tick", tickActions);
}

d3.json('data/nodes_and_links.json', function (error, data) {
    if (error) throw error;
    drawGraph(data);
});
