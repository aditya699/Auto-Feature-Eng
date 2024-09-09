document.addEventListener('DOMContentLoaded', function() {
    const uploadBtn = document.getElementById('uploadBtn');
    const csvFile = document.getElementById('csvFile');
    const status = document.getElementById('status');
    const errorMessage = document.getElementById('error-message');

    uploadBtn.addEventListener('click', uploadFile);

    function uploadFile() {
        const file = csvFile.files[0];
        if (!file) {
            showError('Please select a CSV file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                status.textContent = 'File uploaded successfully';
                status.style.display = 'block';
                errorMessage.style.display = 'none';
                createDashboard(data);
            }
        })
        .catch(error => {
            showError('An error occurred while uploading the file');
            console.error('Error:', error);
        });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        status.style.display = 'none';
    }
});

function createDashboard(data) {
    const margin = {top: 40, right: 150, bottom: 60, left: 60};
    const width = 800 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select("#dashboard")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .range([height, 0]);

    const color = d3.scaleOrdinal()
        .domain(data.categories)
        .range(d3.schemeCategory10);

    x.domain(data.columns);
    y.domain([0, d3.max(data.data, d => d.value)]);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Bars
    svg.selectAll(".bar")
        .data(data.data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.name))
        .attr("y", d => y(d.value))
        .attr("width", x.bandwidth() / data.categories.length)
        .attr("height", d => height - y(d.value))
        .attr("fill", d => color(d.category))
        .attr("transform", d => `translate(${(x.bandwidth() / data.categories.length) * data.categories.indexOf(d.category)}, 0)`)
        .on("mouseover", function(event, d) {
            d3.select(this).attr("opacity", 0.8);
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(`${data.filterColumn}: ${d.category}<br/>${d.name}: ${d.value.toFixed(2)}`)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function(d) {
            d3.select(this).attr("opacity", 1);
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

    // Legend
    const legend = svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .attr("text-anchor", "end")
        .selectAll("g")
        .data(color.domain().slice().reverse())
        .enter().append("g")
        .attr("transform", (d, i) => `translate(0,${i * 20})`);

    legend.append("rect")
        .attr("x", width + 130)
        .attr("width", 19)
        .attr("height", 19)
        .attr("fill", color);

    legend.append("text")
        .attr("x", width + 125)
        .attr("y", 9.5)
        .attr("dy", "0.32em")
        .text(d => d);

    // Tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    // Filter functionality
    d3.select("#filter")
        .append("label")
        .text(data.filterColumn + ": ")
        .append("select")
        .on("change", updateChart)
        .selectAll("option")
        .data(["All", ...data.categories])
        .enter()
        .append("option")
        .text(d => d);

    function updateChart() {
        const selectedCategory = d3.select("#filter select").property("value");
        
        svg.selectAll(".bar")
            .style("display", d => selectedCategory === "All" || d.category === selectedCategory ? null : "none");
    }
}