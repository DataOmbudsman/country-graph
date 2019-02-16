var width = 960,
    height = 500

var svg = d3.select("svg")
    .attr("class", "map")
    .attr("width", width)
    .attr("height", height);

var simulation = d3.forceSimulation()
    .force("charge_force", d3.forceManyBody().strength(-25))
    .force("center_force", d3.forceCenter(width / 2, height / 2))
    .force("links", d3.forceLink().id(nodeName).distance(linkDistance))
    .force("collide", d3.forceCollide(collisionRadius))
    ;

var voronoi = d3.voronoi()
    .x(function (d) { return d.x; })
    .y(function (d) { return d.y; })
    .extent([[width * -100, height * -100], [width * 100, height * 100]]);

var zoom = d3.zoom();

var panMode = true;

var colorMapping = {
    "Africa": "#FF6347",
    "Asia": "#DCDCDC",
    "Europe": "#8FBC8F",
    "North_America": "#BA55D3",
    "Oceania": "#1E90FF",
    "South_America": "#FFA500",
    "Multi": "#FFD700",
}

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

function nodeName(d) {
    return d.name;
}

function linkDistance(d) {
    return d.border / 100;
}

function colorOfCircle(d) {
    var key = d.continents.length > 1 ? "Multi" : d.continents[0]
    return colorMapping[key]
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
        .selectAll("nodes")
        .data(graph.nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", highlightStart)
        .on("mouseout", highlightEnd);

    var circle = node
        .append("circle")
        .attr("r", sizeOfCircle)
        .attr("fill", colorOfCircle);

    var label = node
        .append("text")
        .attr("dy", ".35em")
        .text(nodeName)
        .style("pointer-events", "none");

    var cell = node
        .append("path")
        .attr("class", "cell");

    function switchPanMode() {
        var newPointerEvents = panMode ? "all" : "none";
        var newCursorStyle = panMode ? "default" : "move";
        cell.style("pointer-events", newPointerEvents);
        svg.style("cursor", newCursorStyle);
        panMode = !panMode
    }

    function zoomActions() {
        g.attr("transform", d3.event.transform)
    }

    function tickActions() {
        cell
            .data(voronoi.polygons(graph.nodes))
            .attr("d", function (d) { return d.length ? "M" + d.join("L") : null; });

        circle
            .attr("cx", function (d) { return d.x; })
            .attr("cy", function (d) { return d.y; });

        link
            .attr("x1", function (d) { return d.source.x; })
            .attr("y1", function (d) { return d.source.y; })
            .attr("x2", function (d) { return d.target.x; })
            .attr("y2", function (d) { return d.target.y; });

        label
            .attr("x", function (d) { return d.x + 20; })
            .attr("y", function (d) { return d.y; });
    }

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.33).restart();
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

    var linkSet = {};
    graph.links.forEach(function (link) {
        linkSet[link.source + "," + link.target] = true;
    });

    function areLinked(nodeA, nodeB) {
        return (
            linkSet[nodeA.name + "," + nodeB.name] ||
            linkSet[nodeB.name + "," + nodeA.name] ||
            nodeA.name == nodeB.name
        );
    }

    function highlightStart(highlightedNode) {
        var targetOpacity = 0.2;
        node
            .filter((node) => !areLinked(highlightedNode, node))
            .attr("fill-opacity", targetOpacity)
            .style("stroke-opacity", targetOpacity);

        label
            .filter((node) => areLinked(highlightedNode, node))
            .style("display", "inline");

        link
            .filter((link) => link.source != highlightedNode && link.target != highlightedNode)
            .style("stroke-opacity", targetOpacity);
    }

    function highlightEnd() {
        node
            .style("stroke-opacity", 1)
            .attr("fill-opacity", 1);

        label
            .style("display", "none");

        link
            .style("stroke-opacity", 1);
    }

    d3.select("body").on("keydown", () => {
        if (d3.event.keyCode === 32) switchPanMode()
    });

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
