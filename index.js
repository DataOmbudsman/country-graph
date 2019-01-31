var width = 960,
    height = 500

var svg = d3.select("svg")
    .attr("width", width)
    .attr("height", height);

var simulation = d3.forceSimulation()
    .force("charge_force", d3.forceManyBody().strength(-15))
    .force("center_force", d3.forceCenter(width / 2, height / 2))
    .force("links", d3.forceLink().id(function (d) { return d.name; }));
    .force("collide", d3.forceCollide(collisionRadius))
    ;

var zoom = d3.zoom();

function sizeOfCircle(d) {
    let min_size = 6;
    let max_size = 16;
    let max_neighbor_count = 14;

    var normalized = d.neighbor_count / max_neighbor_count;
    return min_size + normalized * (max_size - min_size)
}

function collisionRadius(d) {
    return d.neighbor_count * 4;
}

function drawGraph(graph) {
    var g = svg.append("g")
        .attr("class", "everything");

    var link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter()
        .append("line");

    var node = g.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter()
        .append("circle")
        .attr("r", sizeOfCircle)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    function zoomActions() {
        g.attr("transform", d3.event.transform)
    }

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

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.1).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    simulation
        .on("tick", tickActions)
        .nodes(graph.nodes)
        .force("links")
        .links(graph.links);

    zoom.on("zoom", zoomActions)(svg);
}

d3.json('data/nodes_and_links.json', function (error, data) {
    if (error) throw error;
    drawGraph(data);
});